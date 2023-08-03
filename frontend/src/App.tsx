import React from 'react';
import './App.css';


import { Route, Routes } from 'react-router-dom';
import Portfolio from './pages/Portfolio';
import Holdings from './pages/Holdings';

function App() {
  const [mobileOpen, setMobileOpen] = React.useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  return (
      <Routes>
        <Route path="/" element={< Portfolio mobileOpen={mobileOpen} handleDrawerToggle={handleDrawerToggle}  />}> 
        </Route>
        <Route path="/holdings" element={< Holdings mobileOpen={mobileOpen} handleDrawerToggle={handleDrawerToggle}  />}>
        </Route>
      </Routes>
  );
}

export default App;
