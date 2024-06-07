import React from 'react'
import Container from 'react-bootstrap/esm/Container'
import { Canvas } from '@react-three/fiber'

export default function THREEViz() {
    return (
        <Container
            fluid
            className='h-100 d-flex align-items-center justify-content-center'
            style={{ position: 'absolute', zIndex: 0 }}
        >
            <Canvas>
                <ambientLight intensity={1} />
                <mesh position={[0, 0, 0]}>
                    <boxGeometry args={[1, 1, 0]} />
                    <meshStandardMaterial wireframe={true} color={"#fff"} />
                </mesh>
            </Canvas>
        </Container>
    )
}