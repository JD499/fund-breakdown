import {AppBarComponent} from '../components/AppBarComponent';
import {DrawerComponent} from '../components/DrawerComponent';
import {HoldingsDisplay} from '../components/HoldingsDisplay';
import {HoldingsItem} from "../App.tsx";


interface HoldingsProps {
    mobileOpen: boolean;
    handleDrawerToggle: () => void;
    holdings: HoldingsItem[];
}

function Holdings(props: HoldingsProps) {
    return (
        <div>
            <AppBarComponent handleDrawerToggle={props.handleDrawerToggle}/>
            <DrawerComponent mobileOpen={props.mobileOpen} handleDrawerToggle={props.handleDrawerToggle}/>
            <HoldingsDisplay holdings={props.holdings}/>
        </div>
    );
}


export default Holdings;