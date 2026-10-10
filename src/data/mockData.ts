import {
  Apple,
  BookOpen,
  Brain,
  BriefcaseBusiness,
  Building2,
  CircleHelp,
  ClipboardCheck,
  GraduationCap,
  HandHelping,
  HeartPulse,
  MapPinned,
  ShieldCheck,
  Sparkles,
  Stethoscope,
  UserRound,
  Users,
  Utensils,
} from 'lucide-react'
import type { NavItem, ServiceGroup, ServiceItem, StepItem, UserGroup } from '../types'

export const navItems: NavItem[] = [
  { label: 'Home', to: '/' },
  { label: 'About', to: '/about' },
  { label: 'Services', to: '/services' },
  { label: 'How It Works', to: '/how-it-works' },
  { label: 'Help', to: '/help' },
]

export const featuredServices: ServiceItem[] = [
  {
    title: 'Education Continuity',
    description: 'Support school transitions, enrollment follow-up and education continuity after migration.',
    icon: GraduationCap,
  },
  {
    title: 'Healthcare Continuity',
    description: 'Help families maintain healthcare follow-ups and discover nearby health services.',
    icon: HeartPulse,
  },
  {
    title: 'Nutrition & Food',
    description: 'Help children continue accessing appropriate nutrition and food-support services.',
    icon: Apple,
  },
  {
    title: 'Child Protection',
    description: 'Connect authorized support workers and families with child-protection services.',
    icon: ShieldCheck,
  },
  {
    title: 'Well-being',
    description: 'Provide access to counselling and child well-being support resources.',
    icon: Brain,
  },
  {
    title: 'Social Support',
    description: 'Help families discover relevant government, community and social-support services.',
    icon: HandHelping,
  },
  {
    title: 'GIS Service Finder',
    description: 'Find relevant schools, healthcare facilities and support services near the family’s new location.',
    icon: MapPinned,
  },
]

export const serviceGroups: ServiceGroup[] = [
  {
    title: 'Child Services',
    services: [
      { title: 'Education', description: 'School continuity and transfer coordination.', icon: GraduationCap },
      { title: 'Healthcare', description: 'Medical follow-up tracking and referrals.', icon: HeartPulse },
      { title: 'Nutrition', description: 'Food support and nutrition follow-ups.', icon: Utensils },
      { title: 'Protection', description: 'Safeguarding and protection case support.', icon: ShieldCheck },
      { title: 'Well-being', description: 'Counselling and emotional support access.', icon: Brain },
      { title: 'Inclusion', description: 'Disability and inclusion-focused support planning.', icon: Users },
    ],
  },
  {
    title: 'Family Services',
    services: [
      { title: 'Migration update', description: 'Capture changes in family location and needs.', icon: MapPinned },
      { title: 'Service discovery', description: 'Locate relevant schools and support services nearby.', icon: BookOpen },
      { title: 'Government-service information', description: 'Share updates on available public assistance.', icon: BriefcaseBusiness },
      { title: 'Help requests', description: 'Raise needs and follow-up support requests.', icon: CircleHelp },
    ],
  },
  {
    title: 'Organization Services',
    services: [
      { title: 'School coordination', description: 'Facilitate transfer and continuity workflows.', icon: Building2 },
      { title: 'Healthcare coordination', description: 'Coordinate service providers and referrals.', icon: Stethoscope },
      { title: 'NGO/social-worker case management', description: 'Monitor support plans and case updates.', icon: ClipboardCheck },
    ],
  },
  {
    title: 'Government Services',
    services: [
      { title: 'Aggregate analytics', description: 'Understand service coverage and gaps.', icon: Users },
      { title: 'GIS insights', description: 'Map service access patterns and areas of need.', icon: MapPinned },
      { title: 'Demand forecasting', description: 'Plan resource allocation and service capacity.', icon: Sparkles },
    ],
  },
]

export const howItWorksSteps: StepItem[] = [
  {
    number: '01',
    title: 'Register Family',
    description: 'Create a secure family profile.',
  },
  {
    number: '02',
    title: 'Add Child Information',
    description: 'Record essential education, healthcare and support information.',
  },
  {
    number: '03',
    title: 'Update Migration',
    description: 'Tell the platform when your family moves to a new location.',
  },
  {
    number: '04',
    title: 'Continue Services',
    description: 'Receive relevant service information, follow-ups and recommendations.',
  },
]

export const userGroups: UserGroup[] = [
  {
    title: 'Families',
    description: 'Manage child service continuity and discover support.',
    icon: UserRound,
  },
  {
    title: 'Schools',
    description: 'Support education continuity and transfer coordination.',
    icon: GraduationCap,
  },
  {
    title: 'NGOs & Social Workers',
    description: 'Coordinate authorized cases and follow-ups.',
    icon: HandHelping,
  },
  {
    title: 'Government',
    description: 'Use aggregated insights for planning and resource allocation.',
    icon: Building2,
  },
]

export const languages = ['English', 'Marathi', 'Hindi']
