import { useEffect, useRef } from 'react'
import { Circle, CircleMarker, MapContainer, Marker, Popup, TileLayer, Tooltip, useMap } from 'react-leaflet'
import { divIcon, latLng, type Marker as LeafletMarker } from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { formatLabel, verificationLabel, type NearbyService } from '../api/services'

type Props = {
  center: { latitude: number; longitude: number }
  radiusKm: number
  services: NearbyService[]
  selectedId: string | null
  onSelect: (serviceId: string) => void
  className?: string
}

type MarkerRefs = React.RefObject<Record<string, LeafletMarker | null>>

// A CSS-drawn pin, so no image files are needed.
function pinIcon(selected: boolean) {
  const size = selected ? 30 : 24
  const color = selected ? '#d97706' : '#0f766e'
  return divIcon({
    className: 'sahaayak-pin',
    html: `<span style="display:block;width:${size}px;height:${size}px;border-radius:50% 50% 50% 0;transform:rotate(-45deg);background:${color};border:2px solid #fff;box-shadow:0 1px 5px rgba(0,0,0,.45)"></span>`,
    iconSize: [size, size],
    iconAnchor: [size / 2, size],
    popupAnchor: [0, -size],
  })
}

function FitToSearch({ latitude, longitude, radiusKm }: { latitude: number; longitude: number; radiusKm: number }) {
  const map = useMap()
  useEffect(() => {
    map.fitBounds(latLng(latitude, longitude).toBounds(radiusKm * 2000), { animate: false })
  }, [map, latitude, longitude, radiusKm])
  return null
}

function FocusSelected({ services, selectedId, markerRefs }: { services: NearbyService[]; selectedId: string | null; markerRefs: MarkerRefs }) {
  const map = useMap()
  useEffect(() => {
    if (!selectedId) return
    const item = services.find((service) => service.service_id === selectedId)
    if (!item || item.latitude === null || item.longitude === null) return
    map.flyTo([item.latitude, item.longitude], Math.max(map.getZoom(), 14), { duration: 0.6 })
    markerRefs.current[selectedId]?.openPopup()
  }, [map, services, selectedId, markerRefs])
  return null
}

export function ServiceMap({ center, radiusKm, services, selectedId, onSelect, className = 'h-[420px] w-full' }: Props) {
  const markerRefs = useRef<Record<string, LeafletMarker | null>>({})
  const mappable = services.filter((service) => service.latitude !== null && service.longitude !== null)

  return (
    <MapContainer
      center={[center.latitude, center.longitude]}
      zoom={12}
      scrollWheelZoom
      className={`z-0 rounded-2xl ${className}`}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        maxZoom={19}
      />
      <FitToSearch latitude={center.latitude} longitude={center.longitude} radiusKm={radiusKm} />
      <FocusSelected services={mappable} selectedId={selectedId} markerRefs={markerRefs} />

      <Circle
        center={[center.latitude, center.longitude]}
        radius={radiusKm * 1000}
        pathOptions={{ color: '#0f766e', weight: 1, fillOpacity: 0.05 }}
      />
      <CircleMarker
        center={[center.latitude, center.longitude]}
        radius={7}
        pathOptions={{ color: '#ffffff', weight: 2, fillColor: '#2563eb', fillOpacity: 1 }}
      >
        <Tooltip>Search point</Tooltip>
      </CircleMarker>

      {mappable.map((service) => (
        <Marker
          key={service.service_id}
          position={[service.latitude as number, service.longitude as number]}
          icon={pinIcon(service.service_id === selectedId)}
          zIndexOffset={service.service_id === selectedId ? 1000 : 0}
          ref={(marker) => {
            markerRefs.current[service.service_id] = marker
          }}
          eventHandlers={{ click: () => onSelect(service.service_id) }}
        >
          <Popup>
            <div className="space-y-1 text-sm">
              <p className="font-bold text-slate-900">{service.organization_name}</p>
              <p className="text-slate-800">{service.service_name}</p>
              <p className="text-slate-600">{formatLabel(service.service_type)}</p>
              <p className="text-slate-600">{service.distance_km} km</p>
              {service.address ? <p className="text-slate-600">{service.address}</p> : null}
              <p className="text-slate-600">
                {[service.city_or_village, service.taluka, service.district].filter(Boolean).join(', ') || 'Location not listed'}
              </p>
              <p className={service.is_verified ? 'font-semibold text-emerald-700' : 'font-semibold text-amber-700'}>
                {verificationLabel(service)}
              </p>
              {service.contact_information ? <p className="text-slate-600">{service.contact_information}</p> : null}
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  )
}