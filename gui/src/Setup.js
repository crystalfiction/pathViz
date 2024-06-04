import react, { useState, useEffect } from 'react'
import Button from 'react-bootstrap/Button'
import Form from 'react-bootstrap/Form'

export default function Setup({ onSetup }) {
    const [doSetup, setDoSetup] = useState()
    const [dfPath, setDfPath] = useState()
    const [result, setResult] = useState()

    function handleSetup(e) {
        e.preventDefault()
        if (e.target.form[0].value === "") return;
        setDfPath(e.target.form[0].value)
        setDoSetup(true)
    }

    // if dfPath exists in state
    useEffect(() => {
        // fetch to see if already set up
        fetch("/setup")
            .then(res => res.json())
            .then(data => setResult(data))
    }, [])

    // when doSetup is changed
    useEffect(() => {
        if (!doSetup && !dfPath) return;
        fetch("/setup?dfPath=" + dfPath, { method: "POST" })
            .then(res => res.json())
            .then(data => setResult(data))
    }, [doSetup, dfPath])

    // when result changes
    useEffect(() => {
        if (!result) return;
        // if result is found...
        if (result['isSetup'] === true) {
            setDoSetup(false)
            return onSetup(true)
        }
        else {
            setDoSetup(false)
            return onSetup(false)
        }
    }, [result, onSetup])


    return (
        <>
            <Form className='w-50'>
                <div className='mb-3'>
                    <Form.Label className='mb-2' style={{ lineHeight: 1.2 }}>Enter the path to your Dwarf Fortress game directory</Form.Label>
                    <Form.Control />
                    <Form.Text muted>Ex: <code>C:\Users\User\Dwarf Fortress</code></Form.Text>
                </div>
                <Button type="submit" variant='dark' className='w-100 btn-outline-light' onClick={(e) => handleSetup(e)}>Setup</Button>
            </Form>
        </>
    )
}