import { AppBarComponent } from '../components/AppBarComponent';
import { DrawerComponent } from '../components/DrawerComponent';
import { HoldingsDisplay } from '../components/HoldingsDisplay';


interface HoldingsProps {
    mobileOpen: boolean;
    handleDrawerToggle: () => void;
  }

function Holdings(props: HoldingsProps) {
    return (
        <div>
            <AppBarComponent handleDrawerToggle={props.handleDrawerToggle} />
            <DrawerComponent mobileOpen={props.mobileOpen} handleDrawerToggle={props.handleDrawerToggle} />
            <HoldingsDisplay/>
        </div>
    );
}



export default Holdings;