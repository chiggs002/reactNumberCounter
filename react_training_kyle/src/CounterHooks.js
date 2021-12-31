import React, { useState, useContext } from 'react'
import { ThemeContext } from './App'
console.log('TOP IMPORT PASSED THEMECOTEXT  Counter Hooks...START')

export default function CounterHooks({ initialCount }) {
  console.log('Render Counter Hooks...START')
  const [count, setCount] = useState(initialCount)
  const style = useContext(ThemeContext)
  return (
    <div>
      
      <button style={style} onClick={() => setCount(prevCount => prevCount - 1)}>-</button>
      <span>{count}</span>
      <button style={style} onClick={() => setCount(prevCount => prevCount + 1)}>+</button>

    </div>
    
  )
}