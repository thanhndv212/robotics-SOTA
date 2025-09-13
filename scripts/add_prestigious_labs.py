#!/usr/bin/env python3
"""
Script to add prestigious robotics labs from MIT, UC Berkeley, Stanford, CMU, and UW
to the robotics research database.
"""

import requests
import json
import time

# Backend API base URL
API_BASE = "http://127.0.0.1:8080/api"

def add_lab(lab_data):
    """Add a single lab to the database via API"""
    try:
        response = requests.post(f"{API_BASE}/labs", json=lab_data)
        if response.status_code == 201:
            result = response.json()
            print(f"✓ Added: {lab_data['name']}")
            return result
        else:
            print(f"✗ Failed to add {lab_data['name']}: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"✗ Error adding {lab_data['name']}: {e}")
        return None

def add_mit_labs():
    """Add MIT robotics labs"""
    print("\n🏫 Adding MIT Labs...")
    
    mit_labs = [
        {
            "name": "SPARK Lab (Sensing, Perception, Autonomy, and Robot Kinetics)",
            "pi": "Luca Carlone",
            "institution": "MIT",
            "city": "Cambridge",
            "country": "USA",
            "focus_areas": ["perception", "SLAM", "autonomous systems", "multi-robot systems"],
            "website": "http://web.mit.edu/sparklab/",
            "description": "Research in robot perception, SLAM, and multi-robot coordination"
        },
        {
            "name": "Personal Robotics Group",
            "pi": "Cynthia Breazeal",
            "institution": "MIT",
            "city": "Cambridge",
            "country": "USA",
            "focus_areas": ["social robotics", "human-robot interaction", "assistive technology"],
            "website": "https://www.media.mit.edu/groups/personal-robots/overview/",
            "description": "Developing socially intelligent robots for human collaboration"
        },
        {
            "name": "MCube Lab",
            "pi": "Alberto Rodriguez",
            "institution": "MIT",
            "city": "Cambridge",
            "country": "USA",
            "focus_areas": ["manipulation", "contact mechanics", "grasping"],
            "website": "http://mcube.mit.edu/",
            "description": "Research in robotic manipulation and contact-rich interactions"
        },
        {
            "name": "Distributed Robotics Lab",
            "pi": "Daniela Rus",
            "institution": "MIT",
            "city": "Cambridge",
            "country": "USA",
            "focus_areas": ["distributed systems", "swarm robotics", "multi-robot coordination"],
            "website": "http://groups.csail.mit.edu/drl/",
            "description": "Distributed algorithms and multi-robot systems"
        },
        {
            "name": "Robot Locomotion Group",
            "pi": "Russ Tedrake",
            "institution": "MIT",
            "city": "Cambridge",
            "country": "USA",
            "focus_areas": ["locomotion", "dynamic systems", "control theory", "learning"],
            "website": "http://groups.csail.mit.edu/locomotion/",
            "description": "Research in dynamic locomotion and underactuated robotics"
        },
        {
            "name": "Biomimetic Robotics Lab",
            "pi": "Sangbae Kim",
            "institution": "MIT",
            "city": "Cambridge",
            "country": "USA",
            "focus_areas": ["biomimetics", "locomotion", "legged robots"],
            "website": "https://biomimetics.mit.edu/",
            "description": "Bio-inspired robots for dynamic locomotion"
        },
        {
            "name": "Interactive Robotics Group",
            "pi": "Julie Shah",
            "institution": "MIT",
            "city": "Cambridge",
            "country": "USA",
            "focus_areas": ["human-robot collaboration", "manufacturing", "planning"],
            "website": "https://interactive.mit.edu/",
            "description": "Human-robot interaction and collaborative systems"
        },
        {
            "name": "Robust Robotics Group",
            "pi": "Nick Roy",
            "institution": "MIT",
            "city": "Cambridge",
            "country": "USA",
            "focus_areas": ["autonomous navigation", "planning", "UAVs"],
            "website": "http://groups.csail.mit.edu/rrg/",
            "description": "Robust autonomous navigation and planning algorithms"
        },
        {
            "name": "Improbable AI",
            "pi": "Pulkit Agrawal",
            "institution": "MIT",
            "city": "Cambridge",
            "country": "USA",
            "focus_areas": ["artificial intelligence", "learning", "robotics"],
            "website": "https://people.csail.mit.edu/pulkitag/",
            "description": "AI and machine learning for robotics applications"
        },
        {
            "name": "D'Arbeloff Lab: Robotics",
            "pi": "Harry Asada",
            "institution": "MIT",
            "city": "Cambridge",
            "country": "USA",
            "focus_areas": ["robotics", "manufacturing", "automation"],
            "website": "http://darbeloff.mit.edu/",
            "description": "Robotics and manufacturing automation research"
        }
    ]
    
    for lab in mit_labs:
        add_lab(lab)
        time.sleep(0.5)  # Rate limiting

def add_berkeley_labs():
    """Add UC Berkeley robotics labs"""
    print("\n🐻 Adding UC Berkeley Labs...")
    
    berkeley_labs = [
        {
            "name": "AUTOLAB (Laboratory for Automation Science and Engineering)",
            "pi": "Ken Goldberg",
            "institution": "UC Berkeley",
            "city": "Berkeley",
            "country": "USA",
            "focus_areas": ["automation", "grasping", "cloud robotics", "surgical robotics"],
            "website": "http://autolab.berkeley.edu/",
            "description": "Research in robotic automation, grasping, and cloud robotics"
        },
        {
            "name": "Berkeley AI Research Lab (BAIR) - Robotics",
            "pi": "Pieter Abbeel",
            "institution": "UC Berkeley",
            "city": "Berkeley",
            "country": "USA",
            "focus_areas": ["deep learning", "reinforcement learning", "robotics"],
            "website": "http://bair.berkeley.edu/",
            "description": "AI research with focus on deep learning for robotics"
        },
        {
            "name": "Robot Learning Lab",
            "pi": "Sergey Levine",
            "institution": "UC Berkeley",
            "city": "Berkeley",
            "country": "USA",
            "focus_areas": ["robot learning", "deep learning", "reinforcement learning"],
            "website": "https://people.eecs.berkeley.edu/~svlevine/",
            "description": "Deep learning and reinforcement learning for robotics"
        },
        {
            "name": "Human-Robot Interaction Lab",
            "pi": "Anca Dragan",
            "institution": "UC Berkeley",
            "city": "Berkeley",
            "country": "USA",
            "focus_areas": ["human-robot interaction", "motion planning", "assistive robotics"],
            "website": "https://people.eecs.berkeley.edu/~anca/",
            "description": "Human-centered robotics and interaction design"
        },
        {
            "name": "Biomimetic Millisystems Lab",
            "pi": "Ronald Fearing",
            "institution": "UC Berkeley",
            "city": "Berkeley",
            "country": "USA",
            "focus_areas": ["biomimetics", "microrobotics", "micro-manipulation"],
            "website": "http://bml.eecs.berkeley.edu/",
            "description": "Bio-inspired microsystems and microrobotics"
        },
        {
            "name": "Hybrid Systems Lab",
            "pi": "Claire Tomlin",
            "institution": "UC Berkeley",
            "city": "Berkeley",
            "country": "USA",
            "focus_areas": ["hybrid systems", "control theory", "safety verification"],
            "website": "https://people.eecs.berkeley.edu/~tomlin/",
            "description": "Safety verification and control of hybrid systems"
        }
    ]
    
    for lab in berkeley_labs:
        add_lab(lab)
        time.sleep(0.5)

def add_stanford_labs():
    """Add Stanford robotics labs"""
    print("\n🌲 Adding Stanford Labs...")
    
    stanford_labs = [
        {
            "name": "Autonomous Systems Lab (ASL)",
            "pi": "Marco Pavone",
            "institution": "Stanford University",
            "city": "Stanford",
            "country": "USA",
            "focus_areas": ["autonomous vehicles", "motion planning", "control"],
            "website": "https://asl.stanford.edu/",
            "description": "Research in autonomous systems and self-driving vehicles"
        },
        {
            "name": "Assistive Robotics and Manipulation (ARM) Lab",
            "pi": "Monroe Kennedy III",
            "institution": "Stanford University",
            "city": "Stanford",
            "country": "USA",
            "focus_areas": ["assistive robotics", "manipulation", "human-robot interaction"],
            "website": "https://arm.stanford.edu/",
            "description": "Assistive robotics for improving everyday life"
        },
        {
            "name": "Intelligence through Robotic Interaction at Scale (IRIS)",
            "pi": "Chelsea Finn",
            "institution": "Stanford University",
            "city": "Stanford",
            "country": "USA",
            "focus_areas": ["robot learning", "meta-learning", "generalization"],
            "website": "https://irislab.stanford.edu/",
            "description": "Large-scale robot learning and generalization"
        },
        {
            "name": "Biomimetics and Dexterous Manipulation Lab (BDML)",
            "pi": "Mark Cutkosky",
            "institution": "Stanford University",
            "city": "Stanford",
            "country": "USA",
            "focus_areas": ["biomimetics", "dexterous manipulation", "climbing robots"],
            "website": "http://bdml.stanford.edu/",
            "description": "Bio-inspired technologies and dexterous manipulation"
        },
        {
            "name": "Multi-Robot Systems Lab (MSL)",
            "pi": "Mac Schwager",
            "institution": "Stanford University",
            "city": "Stanford",
            "country": "USA",
            "focus_areas": ["multi-robot systems", "swarm robotics", "coordination"],
            "website": "https://msl.stanford.edu/",
            "description": "Multi-robot coordination and swarm intelligence"
        },
        {
            "name": "Stanford Vision and Learning Lab (SVL)",
            "pi": "Fei-Fei Li",
            "institution": "Stanford University",
            "city": "Stanford",
            "country": "USA",
            "focus_areas": ["computer vision", "robot learning", "scene understanding"],
            "website": "https://svl.stanford.edu/",
            "description": "Computer vision and learning for robotics"
        },
        {
            "name": "CHARM Lab",
            "pi": "Allison Okamura",
            "institution": "Stanford University",
            "city": "Stanford",
            "country": "USA",
            "focus_areas": ["haptics", "medical robotics", "teleoperation"],
            "website": "https://charm.stanford.edu/",
            "description": "Haptic interfaces and medical robotics"
        },
        {
            "name": "Robotics Lab",
            "pi": "Oussama Khatib",
            "institution": "Stanford University",
            "city": "Stanford",
            "country": "USA",
            "focus_areas": ["manipulation", "humanoid robotics", "underwater robotics"],
            "website": "https://cs.stanford.edu/group/manips/",
            "description": "Advanced robotics and dexterous manipulation"
        }
    ]
    
    for lab in stanford_labs:
        add_lab(lab)
        time.sleep(0.5)

def add_cmu_labs():
    """Add CMU robotics labs"""
    print("\n🤖 Adding CMU Labs...")
    
    cmu_labs = [
        {
            "name": "AirLab",
            "pi": "Sebastian Scherer",
            "institution": "Carnegie Mellon University",
            "city": "Pittsburgh",
            "country": "USA",
            "focus_areas": ["UAVs", "perception", "autonomous flight"],
            "website": "https://theairlab.org/",
            "description": "Unmanned aerial vehicle research and autonomous flight"
        },
        {
            "name": "Biorobotics Lab",
            "pi": "Howie Choset",
            "institution": "Carnegie Mellon University",
            "city": "Pittsburgh",
            "country": "USA",
            "focus_areas": ["snake robots", "path planning", "medical robotics"],
            "website": "http://biorobotics.ri.cmu.edu/",
            "description": "Bio-inspired robotics and snake-like robots"
        },
        {
            "name": "Intelligent Autonomous Manipulation (IAM) Lab",
            "pi": "Oliver Kroemer",
            "institution": "Carnegie Mellon University",
            "city": "Pittsburgh",
            "country": "USA",
            "focus_areas": ["manipulation", "learning", "grasping"],
            "website": "https://iamlab.ri.cmu.edu/",
            "description": "Intelligent manipulation in unstructured environments"
        },
        {
            "name": "Robot Perception Lab",
            "pi": "Michael Kaess",
            "institution": "Carnegie Mellon University",
            "city": "Pittsburgh",
            "country": "USA",
            "focus_areas": ["SLAM", "state estimation", "perception"],
            "website": "http://rpl.ri.cmu.edu/",
            "description": "Robotic perception and simultaneous localization and mapping"
        },
        {
            "name": "Navlab",
            "pi": "Martial Hebert",
            "institution": "Carnegie Mellon University",
            "city": "Pittsburgh",
            "country": "USA",
            "focus_areas": ["navigation", "computer vision", "autonomous vehicles"],
            "website": "http://www.navlab.net/",
            "description": "Navigation and computer vision for autonomous systems"
        },
        {
            "name": "Human And Robot Partners Lab",
            "pi": "Henny Admoni",
            "institution": "Carnegie Mellon University",
            "city": "Pittsburgh",
            "country": "USA",
            "focus_areas": ["human-robot interaction", "assistive robotics", "social robotics"],
            "website": "https://harp.ri.cmu.edu/",
            "description": "Human-robot partnerships and social interaction"
        },
        {
            "name": "Robotic Exploration Lab",
            "pi": "Zachary Manchester",
            "institution": "Carnegie Mellon University",
            "city": "Pittsburgh",
            "country": "USA",
            "focus_areas": ["space robotics", "control", "optimization"],
            "website": "https://roboticexplorationlab.org/",
            "description": "Robotics for space exploration and extreme environments"
        },
        {
            "name": "Search-based Planning Laboratory",
            "pi": "Maxim Likhachev",
            "institution": "Carnegie Mellon University",
            "city": "Pittsburgh",
            "country": "USA",
            "focus_areas": ["path planning", "search algorithms", "autonomous navigation"],
            "website": "http://sbpl.net/",
            "description": "Search-based planning for robotics applications"
        }
    ]
    
    for lab in cmu_labs:
        add_lab(lab)
        time.sleep(0.5)

def add_uw_labs():
    """Add University of Washington robotics labs"""
    print("\n🌲 Adding UW Labs...")
    
    uw_labs = [
        {
            "name": "Personal Robotics Lab",
            "pi": "Siddhartha Srinivasa",
            "institution": "University of Washington",
            "city": "Seattle",
            "country": "USA",
            "focus_areas": ["manipulation", "human-robot interaction", "assistive robotics"],
            "website": "https://personalrobotics.cs.washington.edu/",
            "description": "Personal robotics for manipulation and human assistance"
        },
        {
            "name": "Robot Learning Lab",
            "pi": "Abhishek Gupta",
            "institution": "University of Washington",
            "city": "Seattle",
            "country": "USA",
            "focus_areas": ["robot learning", "reinforcement learning", "generalization"],
            "website": "https://robotlearning.cs.washington.edu/",
            "description": "Machine learning and AI for robotic systems"
        },
        {
            "name": "Robotics and State Estimation Lab",
            "pi": "Dieter Fox",
            "institution": "University of Washington",
            "city": "Seattle",
            "country": "USA",
            "focus_areas": ["state estimation", "SLAM", "perception"],
            "website": "https://rse-lab.cs.washington.edu/",
            "description": "Robotic perception and state estimation"
        },
        {
            "name": "Sensor Systems Laboratory",
            "pi": "Joshua Smith",
            "institution": "University of Washington",
            "city": "Seattle",
            "country": "USA",
            "focus_areas": ["sensor systems", "wireless power", "RFID"],
            "website": "https://sensor.cs.washington.edu/",
            "description": "Advanced sensor systems for robotics applications"
        }
    ]
    
    for lab in uw_labs:
        add_lab(lab)
        time.sleep(0.5)

def main():
    """Main function to add all labs"""
    print("🚀 Starting to add prestigious robotics labs to database...")
    
    try:
        # Test API connection
        response = requests.get(f"{API_BASE}/labs")
        if response.status_code != 200:
            print("❌ Cannot connect to API. Make sure the backend server is running.")
            return
        
        print("✅ API connection successful")
        
        # Add labs from each institution
        add_mit_labs()
        add_berkeley_labs()
        add_stanford_labs()
        add_cmu_labs()
        add_uw_labs()
        
        print("\n🎉 Finished adding labs!")
        
        # Get final count
        response = requests.get(f"{API_BASE}/labs")
        labs = response.json()
        print(f"📊 Total labs in database: {len(labs)}")
        
    except KeyboardInterrupt:
        print("\n⏹️  Process interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()