/* eslint-disable */
import { Tabs } from '@chakra-ui/react'
import { FiCamera, FiMonitor } from 'react-icons/fi'
import { sidebarStyles } from './sidebar-styles'
import CameraPanel from './camera-panel'
import ScreenPanel from './screen-panel'

function BottomTab(): JSX.Element {
  return (
    <Tabs.Root 
      defaultValue="camera" 
      variant="plain"
      {...sidebarStyles.bottomTab.container}
    >
      <Tabs.List {...sidebarStyles.bottomTab.list}>
        <Tabs.Trigger value="camera" {...sidebarStyles.bottomTab.trigger}>
          <FiCamera />
          Camera
        </Tabs.Trigger>
        <Tabs.Trigger value="screen" {...sidebarStyles.bottomTab.trigger}>
          <FiMonitor />
          Screen
        </Tabs.Trigger>
      </Tabs.List>

      <Tabs.Content value="camera">
        <CameraPanel />
      </Tabs.Content>
      
      <Tabs.Content value="screen">
        <ScreenPanel />
      </Tabs.Content>
    </Tabs.Root>
  );
}

export default BottomTab
