import { Persona } from '../types';
import LeadershipDashboard from './LeadershipDashboard';
import DeliveryDashboard from './DeliveryDashboard';

export default function DashboardController({ persona }: { persona: Persona }) {
  if (persona === 'leadership') {
    return <LeadershipDashboard />;
  } else {
    return <DeliveryDashboard managerId={persona} />;
  }
}
