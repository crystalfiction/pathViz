import React, { useState, useEffect, Fragment, useRef } from 'react'

import Container from 'react-bootstrap/Container'
import Row from 'react-bootstrap/Row'
import Col from 'react-bootstrap/Col'
import Stack from 'react-bootstrap/Stack'
import Button from 'react-bootstrap/Button'
import ButtonGroup from 'react-bootstrap/ButtonGroup'
import Form from 'react-bootstrap/Form'

import Plot from 'react-plotly.js'

import { ReactTyped } from 'react-typed'

import Setup from './Setup'

const initModes = [
    'load',
    'viz',
    'stats',
    'snapshot',
    'clear'
]


function now() {
    const date = new Date()
    const year = date.getFullYear()
    const month = "0" + date.getMonth()
    const day = "0" + date.getDate()
    const time = date.getHours().toString() + date.getMinutes().toString() + date.getSeconds().toString()
    const now = year + month + day + time
    return now
}

function GUI() {
    // gui state
    const [loading, setLoading] = useState(true)
    const [isSetup, setIsSetup] = useState()
    const [modeBtns, setModeBtns] = useState()
    const [currMode, setCurrMode] = useState()
    const [apiResult, setApiResult] = useState()
    const [fakeLog, setFakeLog] = useState([])
    const [loaded, setLoaded] = useState(null)
    const [params, setParams] = useState({
        g: false,
        c: false,
        heat: false,
        limit: 0,
        orient: "btm"
    })

    // gui refs
    const fakeLogWindow = useRef()
    const modeRef = useRef()
    const logHist = useRef([])

    function handleMode(e) {
        e.preventDefault()

        // get clicked button value
        let newMode = e.target.id
        // set currMode to clicked mode
        setCurrMode(newMode)
    }

    // on mode change...
    useEffect(() => {
        // if load
        if (currMode === "load") {
            // try to load data
            const apiLoad = async () => {
                setFakeLog(
                    (curr) => ([
                        "Loading..."
                    ])
                )
                const response = await fetch("/api?mode=load", { method: "POST" });
                const data = await response.json();
                const dataObj = await { data }['data'];

                // after api fetch
                setApiResult(dataObj)
                const verbose = dataObj.verbose
                setFakeLog(
                    (curr) => ([
                        now() + ": " + verbose
                    ])
                )
            }

            // call the fetch function
            apiLoad()
        }
        else if (currMode === "viz") {
            setFakeLog(
                (curr) => ([
                    "Loading..."
                ])
            )
            fetch("/api?mode=viz", { method: "POST" })
                .then(res => res.json())
                .then(data => {
                    const dataObj = { data }['data']
                    setApiResult(dataObj)
                    if (dataObj.status === true)
                        setFakeLog(
                            (curr) => ([
                                now() + ": " + "Visualizing..."
                            ])
                        )
                    else
                        setFakeLog(
                            (curr) => ([
                                now() + ": " + dataObj.verbose
                            ])
                        )
                })
        }
        else if (currMode === "stats") {
            fetch("/api?mode=stats", { method: "POST" })
                .then((res) => res.json())
                .then((data) => {
                    const dataObj = { data }['data']
                    setApiResult(dataObj)
                    const stats = dataObj.verbose
                    setFakeLog(
                        (curr) => ([
                            now() + ": " + stats + "\n---" + "\nPlease be aware that stats files are generated on EVERY call to 'stats'."
                        ])
                    )
                })
        }
        else if (currMode === "snapshot") {
            fetch("/api?mode=snapshot", { method: "POST" })
                .then((res) => res.json())
                .then((data) => {
                    const dataObj = { data }['data']
                    setApiResult(dataObj)
                    const verbose = dataObj.verbose
                    setFakeLog(
                        (curr) => ([
                            now() + ": " + verbose
                        ])
                    )
                })
        }
        else if (currMode === "clear") {
            // try to clear the data
            fetch("/api?mode=clear", { method: "POST" })
                .then((res) => res.json())
                .then((data) => {
                    const dataObj = { data }['data']
                    setApiResult(dataObj)
                    const status = dataObj.verbose
                    setFakeLog(
                        (curr) => ([
                            now() + ": " + status
                        ])
                    )
                })
        }

        setLoading(false)

    }, [currMode, setApiResult, setFakeLog])

    // on currMode change, update modeRef.current
    // aka last mode selected
    useEffect(() => {
        if (currMode) {
            // update modeRef
            modeRef.current = currMode
            // reset currMode
            setCurrMode()
        }
    }, [currMode])

    // render modeBtns when isSetup
    useEffect(() => {
        if (!isSetup) return;
        let newModeBtns = (
            <ButtonGroup>
                {initModes.map((m, i) => (
                    <Fragment key={i}>
                        <Button variant='dark' className='btn-outline-light' id={m} onClick={(e) => handleMode(e)}>{m.toUpperCase()}</Button>
                    </Fragment>
                ))}
            </ButtonGroup>
        )
        setModeBtns(newModeBtns)
    }, [isSetup])

    // if fakeLog changes
    useEffect(() => {
        if (!fakeLog[0]) return;
        if (fakeLog[0] === "Loading...") return;
        // then push last update to hist
        logHist.current = [...new Set([...logHist.current, ...fakeLog])]
    }, [fakeLog])

    // when apiResult is updated...
    useEffect(() => {
        if (!apiResult) return;
        if (!params) return;
        // check if data exists
        if (apiResult.data !== "") {
            // if data not blank setLoaded flag true
            return setLoaded(true)
        }
        else {
            // else set false
            return setLoaded(false)
        }
    }, [apiResult, setLoaded])

    if (loading) return (
        <Container fluid className='h-100 d-flex align-items-center justify-content-center'>
            <Row className='w-25 h-50'>
                <Stack gap={3} className='w-100 h-100 d-flex justify-content-center align-items-center'>
                    <ReactTyped style={{ whiteSpace: "pre-line" }} strings={["Loading..."]} typeSpeed={20} loop={true} />
                </Stack>
            </Row>
        </Container>
    )

    return (
        <Container fluid className='w-100 h-100 d-flex align-items-center justify-content-center'>
            {logHist.current[0] && (
                <div className='position-fixed w-25 start-0 bottom-0 fst-italic mb-1 ms-2 p-2 shadow-lg' style={{ lineHeight: 1.2, opacity: 0.9, backgroundColor: "rgba(0, 0, 0, 0.7)" }}>
                    {logHist.current.length && logHist.current.map((l, i) => <p key={i} className='m-0'>{l}</p>)}
                </div>
            )}
            <Row className='w-50 h-75'>
                <Stack gap={3} className='w-100 h-100 d-flex justify-content-center align-items-center'>
                    <h1 className='display-1 mb-0'>pathViz</h1>
                    <hr className='w-50 m-0' />
                    {!isSetup ? (
                        // not setup
                        <Setup onSetup={(v) => setIsSetup(v)} />
                    ) : (
                        // is setup
                        <>
                            {!modeRef.current && (
                                <div className='w-50' style={{ lineHeight: 1.2 }}>
                                    <p>
                                        Open the in-game dfhack console, via <code>ctrl-shift-p</code>, then run <code>enable logPaths</code> to start logging data.
                                    </p>
                                    <p className='fst-italic'>
                                        Ensure there are existing logs in the <code>data/</code> directory (specified in the <code>.env</code> file) before running load.
                                    </p>
                                </div>
                            )}
                            {fakeLog[0] && (
                                <div className='w-50 mh-25 mb-1' style={{ textTransform: "uppercase" }}>
                                    <div ref={fakeLogWindow} className='w-100 mh-25 p-2 shadow overflow-y-auto overflow-x-hidden border' style={{ lineHeight: 1.2 }}>
                                        <ReactTyped style={{ whiteSpace: "pre-line" }} strings={fakeLog} typeSpeed={10} />
                                    </div>
                                </div>
                            )}
                            {modeBtns}
                            <Button variant='dark' className='m-0 p-1 text-light' style={{ lineHeight: 1, fontSize: "80%", textDecoration: "none" }} onClick={() => window.open("https://github.com/crystalfiction/pathViz/blob/main/README.md", "_blank")}><code>DOCS</code></Button>
                        </>
                    )}
                </Stack>
            </Row>
            {apiResult && (
                apiResult.fig && (
                    <Row className='h-100 py-3' style={{ zIndex: 1, width: "80%" }}>
                        <Plot
                            className='w-100 h-100'
                            data={JSON.parse(apiResult.fig).data}
                            layout={JSON.parse(apiResult.layout)}
                            onInitialized={(figure) => this.setState(figure)}
                            onUpdate={(figure) => this.setState(figure)}
                        />
                    </Row>
                )
            )}
        </Container>
    );
}

export default GUI;
