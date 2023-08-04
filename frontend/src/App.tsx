import React, {useState} from 'react';
import './App.css';
import {Route, Routes} from 'react-router-dom';
import Portfolio from './pages/Portfolio';
import Holdings from './pages/Holdings';

export interface HoldingsItem {
    name: string;
    weighting: number;
    price: number;
    value: number;
}

function App() {
    const [mobileOpen, setMobileOpen] = React.useState(false);
    const [holdings, setHoldings] = useState<HoldingsItem[]>([]);

    const handleDrawerToggle = () => {
        setMobileOpen(!mobileOpen);
    };

    return (
        <Routes>
            <Route path="/" element={<Portfolio mobileOpen={mobileOpen} handleDrawerToggle={handleDrawerToggle}
                                                setHoldings={setHoldings}/>}/>
            <Route path="/holdings" element={<Holdings mobileOpen={mobileOpen} handleDrawerToggle={handleDrawerToggle}
                                                       holdings={holdings}/>}/>
        </Routes>
    );
}

export default App;
