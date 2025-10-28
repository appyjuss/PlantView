import { useState } from 'react'
import leafLogo from './assets/leaflogo.svg'
import './App.css'




function App() {
  const [file, setFile] = useState(null)

  const handleUpload = () => {
    const fd = new FormData()
    fd.append('file', file)

    fetch('http://127.0.0.1:8080/', {
      method: "POST",
      body:fd
    })
    // .then(res => res.json())
    .then(data => console.log(data))
  }


  return (
    <>
      <div className ='logo'>
          <img src={leafLogo} className="plantview logo" alt="plantview logo" />
      </div>
      <div className='App'>

        <h1>Image Upload</h1>

        <input type="file" onChange={ (event) => {
          setFile(event.target.files[0]) } } />
          <button onClick={ handleUpload } >upload</button>
      </div>
    </>
  )
}

export default App
