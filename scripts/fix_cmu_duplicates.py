#!/usr/bin/env python3
"""
Fix CMU/Carnegie Mellon University duplicate institution names.
CMU and Carnegie Mellon University are the same institution.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import create_app, db
from app.models import Lab

def fix_cmu_duplicates():
    """Fix CMU/Carnegie Mellon University duplicates"""
    app = create_app()
    
    with app.app_context():
        print("🔍 Checking for CMU/Carnegie Mellon University duplicates...")
        
        # Find all Carnegie Mellon entries
        carnegie_labs = Lab.query.filter(Lab.institution.like('%Carnegie%')).all()
        cmu_labs = Lab.query.filter(Lab.institution.like('%CMU%')).all()
        
        print(f"\nFound {len(carnegie_labs)} Carnegie Mellon entries:")
        for lab in carnegie_labs:
            print(f"  ID: {lab.id}, Name: {lab.name}, Institution: {lab.institution}, PI: {lab.pi}")
        
        print(f"\nFound {len(cmu_labs)} CMU entries:")
        for lab in cmu_labs:
            print(f"  ID: {lab.id}, Name: {lab.name}, Institution: {lab.institution}, PI: {lab.pi}")
        
        # Find the parent Carnegie Mellon University department
        parent_dept = Lab.query.filter(
            Lab.institution == 'Carnegie Mellon University',
            Lab.lab_type == 'department'
        ).first()
        
        if not parent_dept:
            print("\n❌ No Carnegie Mellon University department found. Creating one...")
            # Find a suitable parent (the one with "Multiple Research Groups")
            parent_candidate = Lab.query.filter(
                Lab.institution == 'Carnegie Mellon University',
                Lab.pi.like('%Multiple%')
            ).first()
            
            if parent_candidate:
                parent_candidate.lab_type = 'department'
                parent_dept = parent_candidate
                print(f"✅ Updated lab ID {parent_dept.id} to be department type")
        
        if parent_dept:
            print(f"\n🏛️ Parent department: {parent_dept.name} (ID: {parent_dept.id})")
            
            # Fix CMU entries to become research groups under Carnegie Mellon University
            for cmu_lab in cmu_labs:
                print(f"\n🔧 Fixing CMU lab: {cmu_lab.name}")
                print(f"   Before: Institution='{cmu_lab.institution}', PI='{cmu_lab.pi}'")
                
                # Update institution name
                cmu_lab.institution = 'Carnegie Mellon University'
                
                # Make it a research group under the parent department
                cmu_lab.lab_type = 'group'
                cmu_lab.parent_lab_id = parent_dept.id
                
                # Clean up the name if needed
                if 'CMU' in cmu_lab.name:
                    cmu_lab.name = cmu_lab.name.replace('CMU ', '').replace('CMU', '').strip()
                    if cmu_lab.name.startswith('Robotics & AI'):
                        cmu_lab.name = 'Robotics & AI Lab (Bagnell Lab)'
                
                print(f"   After:  Institution='{cmu_lab.institution}', PI='{cmu_lab.pi}', Type='{cmu_lab.lab_type}', Parent={cmu_lab.parent_lab_id}")
            
            try:
                db.session.commit()
                print("\n✅ Successfully fixed CMU duplicates!")
                
                # Verify the changes
                print("\n🔍 Verification - All Carnegie Mellon entries after fix:")
                all_cmu = Lab.query.filter(Lab.institution == 'Carnegie Mellon University').all()
                for lab in all_cmu:
                    parent_info = f" (Parent: {lab.parent_lab_id})" if lab.parent_lab_id else ""
                    print(f"  ID: {lab.id}, Name: {lab.name}, PI: {lab.pi}, Type: {lab.lab_type}{parent_info}")
                
            except Exception as e:
                db.session.rollback()
                print(f"\n❌ Error committing changes: {str(e)}")
                return False
        else:
            print("\n❌ Could not find or create Carnegie Mellon University parent department")
            return False
    
    return True

if __name__ == '__main__':
    success = fix_cmu_duplicates()
    if success:
        print("\n🎉 CMU duplicate fix completed successfully!")
    else:
        print("\n💥 CMU duplicate fix failed!")
        sys.exit(1)