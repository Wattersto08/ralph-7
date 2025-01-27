from setuptools import setup

package_name = 'ralph_7'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Tom_Watters',
    maintainer_email='tom.j.watters@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'color = ralph_7.color_pub:main',
            'launch_robot = ralph_7.launch_robot.launch'

        ],
    },
)
