# Distributed Image Processing System using Cloud Computing

This project, *Image Processing Distributed System*, utilizes Amazon's AWS to efficiently distribute image processing tasks across multiple virtual machines, ensuring scalability and reliability.
## Features
- Establishes a cloud environment using Amazon's AWS
- Optimizes VM utilization by assigning distinct roles to each VM
- Integrates VMs into the same VPC for synchronized communication
- Sets up SSH for secure authentication between VMs
- Implements security groups and firewall rules for traffic control
- Implements a "Load Balancer" VM to manage user requests asynchronously
- Utilizes MPI-based features for workload distribution across multiple threads
- Implements fault tolerance mechanism with backup VMs for uninterrupted processing
- Monitors VM status using an asynchronous "Ping-pong" concept
- Enhances system scalability to adapt to workload variations
- A user-friendly GUI for easy image upload and progress tracking

## Installation
1. Clone the repository:

   ````shell
   git clone https://github.com/MinaMorgan/Distributed-Image-Processing-System-using-Cloud-Computing
   

2. Navigate to the project directory:

   ````shell
   cd Distributed-Image-Processing-System-using-Cloud-Computing

3. Intialize VMs using the script provided in the document.

4. Copy the files provided into the VM.
   
## Usage
- Configure AWS credentials and access permissions.
- Run the system deployment script to set up the cloud environment.
- Upload images through the user-friendly GUI.
- Track processing progress and monitor system status.
- Refer to the documentation for detailed usage instructions.
## Contributing
Contributions to this project are welcome. If you have any ideas, suggestions, or bug fixes, please open an issue or submit a pull request.
When contributing, please ensure that your code follows the existing coding style and conventions. Add appropriate tests for any new features or bug fixes.

## Acknowledgments
- The project was inspired by the understanding and implementation of distributed computing, cloud technology, and image processing.
- Special thanks to Amazon's AWS for providing the cloud infrastructure.
- The OpenCV library was used extensively for image processing and computer vision operations.
- Appreciation to the open-source community for valuable resources and support.

## Contact
For any questions or inquiries, please contact [rafikghaly2002@gmail.com](mailto:your-email@example.com) or [minammorgan21@gmail.com](mailto:your-email@example.com).


