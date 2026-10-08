// Approximate public city-centre points, used only to choose a map search point from a
// place NAME. These are not family or child coordinates.
export type PlaceCentre = { name: string; latitude: number; longitude: number }

const CENTRES: PlaceCentre[] = [
  { name: 'Mumbai', latitude: 19.076, longitude: 72.8777 },
  { name: 'Thane', latitude: 19.2183, longitude: 72.9781 },
  { name: 'Bhiwandi', latitude: 19.2967, longitude: 73.0631 },
  { name: 'Pune', latitude: 18.5204, longitude: 73.8567 },
  { name: 'Pimpri-Chinchwad', latitude: 18.6298, longitude: 73.7997 },
  { name: 'Nashik', latitude: 19.9975, longitude: 73.7898 },
  { name: 'Malegaon', latitude: 20.5579, longitude: 74.5089 },
  { name: 'Ahilyanagar', latitude: 19.0948, longitude: 74.748 },
  { name: 'Beed', latitude: 18.989, longitude: 75.76 },
  { name: 'Dharashiv', latitude: 18.186, longitude: 76.0419 },
  { name: 'Latur', latitude: 18.4088, longitude: 76.5604 },
  { name: 'Parbhani', latitude: 19.2704, longitude: 76.7747 },
  { name: 'Nanded', latitude: 19.1383, longitude: 77.321 },
  { name: 'Jalna', latitude: 19.8347, longitude: 75.8816 },
  { name: 'Solapur', latitude: 17.6599, longitude: 75.9064 },
]

const ALIASES: Record<string, string> = {
  'pimpri chinchwad': 'pimpri-chinchwad',
  pcmc: 'pimpri-chinchwad',
  ahmednagar: 'ahilyanagar',
  osmanabad: 'dharashiv',
  'mumbai city': 'mumbai',
  'mumbai suburban': 'mumbai',
  bombay: 'mumbai',
}

function normalise(value: string) {
  return value.trim().toLowerCase().replace(/\s+/g, ' ')
}

export function findPlaceCentre(name?: string | null): PlaceCentre | null {
  if (!name) return null
  const key = normalise(name)
  const target = ALIASES[key] ?? key
  return CENTRES.find((centre) => normalise(centre.name) === target) ?? null
}

/** First candidate (most specific first) that matches a known place name, else null. */
export function firstResolvablePlace(candidates: Array<string | null | undefined>): string | null {
  for (const candidate of candidates) {
    const centre = findPlaceCentre(candidate)
    if (centre) return centre.name
  }
  return null
}