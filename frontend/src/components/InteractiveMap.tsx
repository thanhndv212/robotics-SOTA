import React, { useState, useEffect } from 'react';
import { Map } from 'react-map-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

interface Lab {
  id: number;
  name: string;
  pi: string;
  institution: string;
  city: string;
  country: string;
  latitude: number;
  longitude: number;
  focus_areas: string[];
  website?: string;
}

interface InteractiveMapProps {
  labs: Lab[];
  onLabSelect?: (lab: Lab) => void;
}

const InteractiveMap: React.FC<InteractiveMapProps> = ({ labs, onLabSelect }) => {
  const [viewState, setViewState] = useState({
    longitude: 0,
    latitude: 20,
    zoom: 2
  });

  // TODO: Replace with your Mapbox access token
  const MAPBOX_TOKEN = process.env.REACT_APP_MAPBOX_TOKEN || 'YOUR_MAPBOX_TOKEN';

  return (
    <div style={{ height: '600px', width: '100%' }}>
      <Map
        {...viewState}
        onMove={evt => setViewState(evt.viewState)}
        mapStyle="mapbox://styles/mapbox/light-v10"
        mapboxAccessToken={MAPBOX_TOKEN}
      >
        {/* Lab markers will be added here */}
        {labs.map(lab => {
          if (!lab.latitude || !lab.longitude) return null;
          
          return (
            <div
              key={lab.id}
              style={{
                position: 'absolute',
                left: `${((lab.longitude + 180) / 360) * 100}%`,
                top: `${((90 - lab.latitude) / 180) * 100}%`,
                transform: 'translate(-50%, -50%)',
                backgroundColor: '#1890ff',
                borderRadius: '50%',
                width: '12px',
                height: '12px',
                cursor: 'pointer',
                border: '2px solid white',
                boxShadow: '0 2px 4px rgba(0,0,0,0.3)'
              }}
              onClick={() => onLabSelect?.(lab)}
              title={`${lab.name} - ${lab.institution}`}
            />
          );
        })}
      </Map>
    </div>
  );
};

export default InteractiveMap;