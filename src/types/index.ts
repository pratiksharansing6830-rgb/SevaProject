import type { LucideIcon } from 'lucide-react'

export type NavItem = {
  label: string
  to: string
}

export type ServiceItem = {
  title: string
  description: string
  icon: LucideIcon
}

export type ServiceGroup = {
  title: string
  services: ServiceItem[]
}

export type StepItem = {
  number: string
  title: string
  description: string
}

export type UserGroup = {
  title: string
  description: string
  icon: LucideIcon
}

export type ContinuityStatus = 'connected' | 'review' | 'supported' | 'available'

export type ContinuityItem = {
  label: string
  status: ContinuityStatus
}

export type RoleOption = {
  title: string
  description: string
  icon: LucideIcon
}

export type AiCard = {
  title: string
  description: string
  icon: LucideIcon
}

export type MapPoint = {
  title: string
  category: string
  position: string
}

export type FamilyRecord = {
  id: string
  childName: string
  age: number
  className: string
  previousLocation: string
  currentLocation: string
}
