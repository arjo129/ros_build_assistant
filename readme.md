# ros_build_assistant

ROS build assistant acts as a tool to simplify the creation and management of catkin packages.
All you have to do is write source code in python/c++/launch file syntax. The build assistant handles the 
rest of it for you. No more having to write `package.xmls` and editing `cmakefiles`!! Whats more, you will 
automatically get the correct dependencies and the correct build order. You may also use `ros_build_assistant`
as a linter using the  `--lint` option in your CI pipeline. There are also a whole host of ways to script
your builds!


