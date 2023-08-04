import {HoldingsItem} from '../App';
import {AppBarComponent} from '../components/AppBarComponent';
import {DrawerComponent} from '../components/DrawerComponent';
import {MainContent} from '../components/MainContent';


interface PortfolioProps {
    mobileOpen: boolean;
    handleDrawerToggle: () => void;
    setHoldings: React.Dispatch<React.SetStateAction<HoldingsItem[]>>;
}

function Portfolio(props: PortfolioProps) {
    return (
        <div>
            <AppBarComponent handleDrawerToggle={props.handleDrawerToggle}/>
            <DrawerComponent mobileOpen={props.mobileOpen} handleDrawerToggle={props.handleDrawerToggle}/>

            <MainContent setHoldings={props.setHoldings}/>

        </div>
    );
}


export default Portfolio;