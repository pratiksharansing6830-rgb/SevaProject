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
