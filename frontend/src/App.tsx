import './App.css'
import { Box } from '@mui/material'
import ToolCardList from './components/ToolCardList';
import ToolInfo from './components/ToolInfo';
import { Route, Routes } from 'react-router-dom';

// function App() {
//   return (
    <Box 
      sx={{ 
        width: '100vw', 
        height: '100vh', 
        backgroundColor: 'background.default', 
        color: 'text.primary',
        display: 'flex', 
      }}
    >
      {/* <ToolCardList/> */}
      <ToolInfo/>
    </Box>
//   );
// }

function App() {
  return (
    <Box 
    sx={{ 
      width: '100vw', 
      height: '100vh', 
      backgroundColor: 'background.default', 
      color: 'text.primary',
      display: 'flex', 
    }}
  >

    <Routes>
      <Route path="/" element={<ToolCardList />} />
      <Route path="/tool" element={<ToolInfo />} />
    </Routes>
    </Box>

  );
}

export default App;
