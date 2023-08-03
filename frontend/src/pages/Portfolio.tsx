import { AppBarComponent } from '../components/AppBarComponent';
import { DrawerComponent } from '../components/DrawerComponent';
import { MainContent } from '../components/MainContent';


interface PortfolioProps {
    mobileOpen: boolean;
    handleDrawerToggle: () => void;
  }

function Portfolio(props: PortfolioProps) {
    return (
        <div>
            <AppBarComponent handleDrawerToggle={props.handleDrawerToggle} />
            <DrawerComponent mobileOpen={props.mobileOpen} handleDrawerToggle={props.handleDrawerToggle} />
            
            <MainContent />
            
        </div>
    );
}



export default Portfolio;