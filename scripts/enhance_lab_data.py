#!/usr/bin/env python3
"""
Lab data enhancement script to split multi-PI labs into research groups
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import create_app, db
from app.models import Lab
import json


# Research groups mapping for major institutions
RESEARCH_GROUPS = {
    "UC Berkeley": {
        "institution_info": {
            "city": "Berkeley",
            "country": "USA",
            "website": "https://www.berkeley.edu",
            "latitude": 37.8719,
            "longitude": -122.2585
        },
        "groups": [
            {
                "name": "Robot Learning Lab (RLL)",
                "pi": "Pieter Abbeel",
                "focus": ["Deep Reinforcement Learning", "Imitation Learning", "Manipulation"],
                "description": "Research on learning algorithms for robots, with focus on deep RL and imitation learning.",
                "website": "https://rll.berkeley.edu"
            },
            {
                "name": "Berkeley AUTOLAB",
                "pi": "Ken Goldberg",
                "focus": ["Automation", "Cloud Robotics", "Surgical Robotics"],
                "description": "Automation and robotics research with applications in manufacturing and medicine.",
                "website": "https://autolab.berkeley.edu"
            },
            {
                "name": "Levine Lab",
                "pi": "Sergey Levine",
                "focus": ["Robot Learning", "Deep Reinforcement Learning", "Computer Vision"],
                "description": "Machine learning for robotics, focusing on learning from experience.",
                "website": "https://people.eecs.berkeley.edu/~svlevine/"
            },
            {
                "name": "InterACT Lab",
                "pi": "Anca Dragan",
                "focus": ["Human-Robot Interaction", "Legible Motion", "Assistive Robotics"],
                "description": "Research on robots that work alongside and in support of people.",
                "website": "https://interact.berkeley.edu"
            }
        ]
    },
    "Stanford University": {
        "institution_info": {
            "city": "Stanford",
            "country": "USA", 
            "website": "https://www.stanford.edu",
            "latitude": 37.4275,
            "longitude": -122.1697
        },
        "groups": [
            {
                "name": "Stanford IRIS Lab",
                "pi": "Chelsea Finn",
                "focus": ["Meta-Learning", "Robot Learning", "Few-Shot Learning"],
                "description": "Intelligence through Robotic Interaction at Scale - learning algorithms that enable robots to learn efficiently.",
                "website": "https://iris.stanford.edu"
            },
            {
                "name": "Stanford AI Lab (SAIL) - Robotics",
                "pi": "Fei-Fei Li",
                "focus": ["Computer Vision", "Robotics", "AI Safety"],
                "description": "Computer vision and AI research with robotics applications.",
                "website": "https://ai.stanford.edu"
            },
            {
                "name": "Multi-Robot Systems Lab",
                "pi": "Mac Schwager",
                "focus": ["Multi-Robot Systems", "Swarm Robotics", "Autonomous Vehicles"],
                "description": "Coordination and control of teams of autonomous robots.",
                "website": "https://web.stanford.edu/~schwager/"
            }
        ]
    },
    "MIT": {
        "institution_info": {
            "city": "Cambridge",
            "country": "USA",
            "website": "https://www.mit.edu",
            "latitude": 42.3601,
            "longitude": -71.0942
        },
        "groups": [
            {
                "name": "Robot Locomotion Group",
                "pi": "Russ Tedrake",
                "focus": ["Locomotion", "Manipulation", "Underactuated Robotics"],
                "description": "Research on algorithms for highly dynamic robots.",
                "website": "https://groups.csail.mit.edu/locomotion/"
            },
            {
                "name": "Distributed Robotics Lab",
                "pi": "Daniela Rus",
                "focus": ["Multi-Robot Systems", "Soft Robotics", "Autonomous Vehicles"],
                "description": "Research on distributed algorithms for robotics systems.",
                "website": "https://www.csail.mit.edu/research/distributed-robotics-laboratory"
            },
            {
                "name": "Interactive Robotics Group",
                "pi": "Julie Shah",
                "focus": ["Human-Robot Collaboration", "Task Planning", "Manufacturing"],
                "description": "Research on robots that work in teams with people.",
                "website": "https://interactive.mit.edu"
            }
        ]
    },
    "Carnegie Mellon University": {
        "institution_info": {
            "city": "Pittsburgh",
            "country": "USA",
            "website": "https://www.cmu.edu",
            "latitude": 40.4428,
            "longitude": -79.9428
        },
        "groups": [
            {
                "name": "Robot Learning Lab",
                "pi": "Deepak Pathak",
                "focus": ["Self-Supervised Learning", "Exploration", "Embodied AI"],
                "description": "Research on learning algorithms for robotics without human supervision.",
                "website": "https://www.cs.cmu.edu/~dpathak/"
            },
            {
                "name": "Manipulation Lab",
                "pi": "Matthew Mason",
                "focus": ["Manipulation", "Tactile Sensing", "Grasping"],
                "description": "Research on robot manipulation and contact mechanics.",
                "website": "https://www.ri.cmu.edu/ri-faculty/matthew-t-mason/"
            },
            {
                "name": "Field Robotics Center",
                "pi": "Red Whittaker",
                "focus": ["Field Robotics", "Autonomous Vehicles", "Space Robotics"],
                "description": "Research on robots operating in challenging real-world environments.",
                "website": "https://www.ri.cmu.edu/research-center/field-robotics-center/"
            }
        ]
    }
}


def enhance_multi_pi_labs():
    """Split labs with 'multiple PIs' into individual research groups"""
    app = create_app()
    
    with app.app_context():
        # Find labs that need enhancement
        multi_pi_labs = Lab.query.filter(
            (Lab.pi.ilike('%multiple%')) | 
            (Lab.pi.ilike('%various%')) |
            (Lab.pi.ilike('%several%'))
        ).all()
        
        print(f"🔍 Found {len(multi_pi_labs)} labs with multiple PIs to enhance:")
        for lab in multi_pi_labs:
            print(f"   - {lab.name} at {lab.institution}")
        
        enhanced_count = 0
        
        for lab in multi_pi_labs:
            institution_key = None
            
            # Find matching institution
            for key in RESEARCH_GROUPS.keys():
                if key.lower() in lab.institution.lower():
                    institution_key = key
                    break
            
            if not institution_key:
                print(f"❓ No research groups defined for {lab.institution}")
                continue
            
            groups_data = RESEARCH_GROUPS[institution_key]
            
            # Update parent lab to be a department-level entry
            lab.lab_type = 'department'
            lab.pi = f"Multiple Research Groups"
            lab.description = f"Department-level entry containing multiple research groups at {lab.institution}"
            
            print(f"🏢 Converting {lab.institution} to department-level lab")
            
            # Create individual research groups
            for group_info in groups_data["groups"]:
                existing_group = Lab.query.filter_by(
                    name=group_info["name"],
                    institution=lab.institution
                ).first()
                
                if existing_group:
                    print(f"   ⚠️  Research group already exists: {group_info['name']}")
                    continue
                
                research_group = Lab(
                    name=group_info["name"],
                    pi=group_info["pi"],
                    institution=lab.institution,
                    city=lab.city,
                    country=lab.country,
                    website=group_info.get("website", ""),
                    latitude=lab.latitude,
                    longitude=lab.longitude,
                    description=group_info["description"],
                    parent_lab_id=lab.id,
                    lab_type='group'
                )
                
                # Set focus areas
                research_group.focus_areas_list = group_info["focus"]
                
                db.session.add(research_group)
                enhanced_count += 1
                print(f"   ✅ Created: {group_info['name']} (PI: {group_info['pi']})")
        
        try:
            db.session.commit()
            print(f"\n🎉 Successfully enhanced {enhanced_count} research groups!")
            
            # Print summary
            print("\n📊 Enhancement Summary:")
            print("=" * 50)
            departments = Lab.query.filter_by(lab_type='department').all()
            for dept in departments:
                groups = dept.sub_groups.all()
                print(f"\n🏢 {dept.institution}:")
                for group in groups:
                    print(f"   🔬 {group.name} (PI: {group.pi})")
            
            total_groups = sum(dept.sub_groups.count() for dept in departments)
            print(f"\n📈 Total: {len(departments)} departments, {total_groups} research groups")
                    
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error enhancing labs: {e}")
            return False
    
    return True


if __name__ == "__main__":
    success = enhance_multi_pi_labs()
    sys.exit(0 if success else 1)