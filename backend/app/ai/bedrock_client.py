"""
AWS Bedrock client for the CUIA platform.

Improvements:
- Reusable boto3 Session and single shared client (no repeated creation)
- All model parameters configurable via .env
- Smart retry: only retries transient failures (throttle, timeout, network)
- Never retries auth errors, invalid credentials, or invalid model
- Structured logging with request metadata (no sensitive data)
"""

import json
import logging
import os
import time
from typing import Optional, Dict, Any

logger = logging.getLogger("cuia.ai.bedrock")

# ──────────────────────────────────────────────
# Non-retryable error signatures
# ──────────────────────────────────────────────

NON_RETRYABLE_ERRORS = frozenset([
    "AccessDeniedException",
    "UnrecognizedClientException",
    "InvalidIdentityTokenException",
    "ExpiredTokenException",
    "ValidationException",
    "ResourceNotFoundException",
    "ModelNotReadyException",
])

# ──────────────────────────────────────────────
# Retryable error signatures
# ──────────────────────────────────────────────

RETRYABLE_ERRORS = frozenset([
    "ThrottlingException",
    "ServiceUnavailableException",
    "InternalServerException",
    "ModelTimeoutException",
    "RequestTimeoutException",
])


class BedrockClient:
    """
    AWS Bedrock client wrapper with reusable session.

    Supports:
    - Amazon Nova Lite (default)
    - All parameters configurable via environment variables
    - Smart retry with exponential backoff
    - Structured request/response logging (no sensitive data)

    Environment variables:
    - AWS_BEDROCK_MODEL_ID: Model ID (default: amazon.nova-lite-v1:0)
    - AWS_REGION: AWS region (default: us-east-1)
    - AWS_ACCESS_KEY_ID: AWS access key
    - AWS_SECRET_ACCESS_KEY: AWS secret key
    - BEDROCK_MAX_RETRIES: Max retry attempts (default: 2)
    - BEDROCK_TIMEOUT_SECONDS: Request timeout (default: 30)
    - BEDROCK_MAX_TOKENS: Default max response tokens (default: 700)
    - BEDROCK_TEMPERATURE: Sampling temperature (default: 0.05)
    - BEDROCK_TOP_P: Top-P sampling (default: 0.9)
    """

    # Class-level shared session and client
    _shared_session = None
    _shared_client = None
    _shared_region = None

    def __init__(self):
        self.model_id = os.getenv("AWS_BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0")
        self.region = os.getenv("AWS_REGION", "us-east-1")
        self.max_retries = int(os.getenv("BEDROCK_MAX_RETRIES", "2"))
        self.timeout_seconds = int(os.getenv("BEDROCK_TIMEOUT_SECONDS", "30"))
        self.default_max_tokens = int(os.getenv("BEDROCK_MAX_TOKENS", "700"))
        self.temperature = float(os.getenv("BEDROCK_TEMPERATURE", "0.05"))
        self.top_p = float(os.getenv("BEDROCK_TOP_P", "0.9"))

        self._client = None
        self._initialized = False

        try:
            import boto3
            from botocore.config import Config

            # Reuse shared session/client if region matches
            if (BedrockClient._shared_client is not None
                    and BedrockClient._shared_region == self.region):
                self._client = BedrockClient._shared_client
                self._initialized = True
                logger.info(
                    "Bedrock client reused: model=%s, region=%s",
                    self.model_id, self.region
                )
            else:
                # Support new AWS Bedrock long-term API keys (Bearer tokens)
                api_key = os.getenv("BEDROCK_API_KEY")
                if api_key:
                    os.environ["AWS_BEARER_TOKEN_BEDROCK"] = api_key
                    session = boto3.Session(region_name=self.region)
                else:
                    # Create session with standard IAM credentials
                    session = boto3.Session(
                        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                        region_name=self.region,
                    )

                boto_config = Config(
                    read_timeout=self.timeout_seconds,
                    connect_timeout=10,
                    retries={"max_attempts": 0},  # We handle retries ourselves
                )

                self._client = session.client(
                    "bedrock-runtime",
                    config=boto_config,
                )

                # Cache for reuse
                BedrockClient._shared_session = session
                BedrockClient._shared_client = self._client
                BedrockClient._shared_region = self.region

                self._initialized = True
                logger.info(
                    "Bedrock client initialized: model=%s, region=%s, temp=%.2f, topP=%.2f, maxTokens=%d",
                    self.model_id, self.region, self.temperature, self.top_p,
                    self.default_max_tokens
                )

        except ImportError:
            logger.warning("boto3 not installed. Bedrock client unavailable.")
        except Exception as e:
            logger.error("Failed to initialize Bedrock client: %s", str(e))

    @property
    def is_available(self) -> bool:
        """Check if the Bedrock client is ready."""
        return self._initialized and self._client is not None

    def invoke(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
    ) -> str:
        """
        Invoke the Bedrock model with a system prompt and user message.

        Args:
            system_prompt: The system-level instruction.
            user_message: The user's question or input.
            max_tokens: Override default max tokens.
            temperature: Override default temperature.
            top_p: Override default top-p.

        Returns:
            The model's text response.

        Raises:
            RuntimeError: If Bedrock is unavailable or returns a non-retryable error.
        """
        if not self.is_available:
            raise RuntimeError(
                "Bedrock client not available. Check AWS credentials and boto3."
            )

        effective_max_tokens = max_tokens or self.default_max_tokens
        effective_temp = temperature if temperature is not None else self.temperature
        effective_top_p = top_p if top_p is not None else self.top_p

        # Build request body for Amazon Nova Lite
        request_body = {
            "messages": [
                {"role": "user", "content": [{"text": user_message}]}
            ],
            "system": [{"text": system_prompt}],
            "inferenceConfig": {
                "maxTokens": effective_max_tokens,
                "temperature": effective_temp,
                "topP": effective_top_p,
            },
        }

        request_size = len(system_prompt) + len(user_message)
        request_id = f"{self.model_id}:{int(time.time() * 1000) % 100000}"
        start_time = time.monotonic()

        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(
                    "Bedrock request: id=%s, attempt=%d/%d, promptSize=%d, maxTokens=%d",
                    request_id, attempt, self.max_retries,
                    request_size, effective_max_tokens
                )

                response = self._client.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps(request_body),
                    contentType="application/json",
                    accept="application/json",
                )

                response_body = json.loads(response["body"].read())

                # Extract text from Nova response format
                output = response_body.get("output", {})
                message = output.get("message", {})
                content = message.get("content", [])

                text_parts = [c.get("text", "") for c in content if c.get("text")]
                result = " ".join(text_parts).strip()

                latency_ms = int((time.monotonic() - start_time) * 1000)

                if result:
                    logger.info(
                        "Bedrock response: id=%s, responseSize=%d, latency=%dms, retries=%d",
                        request_id, len(result), latency_ms, attempt - 1
                    )
                    return result

                logger.warning(
                    "Bedrock empty response: id=%s, attempt=%d", request_id, attempt
                )

            except Exception as e:
                last_error = e
                error_str = str(e)
                latency_ms = int((time.monotonic() - start_time) * 1000)

                # Check for non-retryable errors
                for err_type in NON_RETRYABLE_ERRORS:
                    if err_type in error_str:
                        logger.error(
                            "Bedrock non-retryable error: id=%s, type=%s, latency=%dms",
                            request_id, err_type, latency_ms
                        )
                        raise RuntimeError(
                            f"Bedrock {err_type}: {error_str}"
                        )

                logger.warning(
                    "Bedrock retryable error: id=%s, attempt=%d/%d, error=%s, latency=%dms",
                    request_id, attempt, self.max_retries, error_str[:100], latency_ms
                )

                # Exponential backoff for retryable errors
                if attempt < self.max_retries:
                    backoff = min(2 ** (attempt - 1), 4)  # 1s, 2s, 4s max
                    time.sleep(backoff)

        latency_ms = int((time.monotonic() - start_time) * 1000)
        logger.error(
            "Bedrock exhausted retries: id=%s, attempts=%d, latency=%dms",
            request_id, self.max_retries, latency_ms
        )
        raise RuntimeError(
            f"Bedrock failed after {self.max_retries} attempts: {str(last_error)}"
        )

    def get_health(self) -> Dict[str, Any]:
        """Return health check information about the Bedrock client."""
        return {
            "status": "healthy" if self.is_available else "unhealthy",
            "provider": "AWS Bedrock",
            "model": self.model_id,
            "region": self.region,
            "initialized": self._initialized,
            "config": {
                "maxTokens": self.default_max_tokens,
                "temperature": self.temperature,
                "topP": self.top_p,
                "maxRetries": self.max_retries,
                "timeout": self.timeout_seconds,
            },
        }
