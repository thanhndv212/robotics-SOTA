#!/usr/bin/env python3
"""
Check for other potential institution naming inconsistencies.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import create_app, db
from app.models import Lab
from collections import defaultdict

def check_institution_naming():
    """Check for potential institution naming inconsistencies"""
    app = create_app()
    
    with app.app_context():
        print("🔍 Checking for institution naming inconsistencies...")
        
        # Get all labs grouped by institution
        all_labs = Lab.query.all()
        institutions = defaultdict(list)
        
        for lab in all_labs:
            institutions[lab.institution].append(lab)
        
        print(f"\nFound {len(institutions)} unique institution names:")
        
        # Look for potential duplicates
        institution_names = list(institutions.keys())
        potential_duplicates = []
        
        for i, inst1 in enumerate(institution_names):
            for j, inst2 in enumerate(institution_names):
                if i >= j:
                    continue
                    
                # Check for similar names
                inst1_lower = inst1.lower()
                inst2_lower = inst2.lower()
                
                # Check various patterns that might indicate duplicates
                if (inst1_lower in inst2_lower or inst2_lower in inst1_lower or
                    abs(len(inst1) - len(inst2)) <= 3 and 
                    sum(c1 != c2 for c1, c2 in zip(inst1_lower, inst2_lower)) <= 2):
                    potential_duplicates.append((inst1, inst2))
        
        if potential_duplicates:
            print(f"\n⚠️  Found {len(potential_duplicates)} potential duplicate pairs:")
            for inst1, inst2 in potential_duplicates:
                print(f"  • '{inst1}' vs '{inst2}'")
                print(f"    Labs: {len(institutions[inst1])} vs {len(institutions[inst2])}")
        else:
            print("\n✅ No obvious naming inconsistencies found!")
        
        # Show all institutions with lab counts
        print(f"\n📊 All institutions (total: {len(institutions)}):")
        for institution, labs in sorted(institutions.items()):
            print(f"  {institution}: {len(labs)} lab(s)")
            if len(labs) > 3:  # Show details for institutions with many labs
                for lab in labs[:3]:
                    print(f"    - {lab.name} ({lab.pi})")
                if len(labs) > 3:
                    print(f"    ... and {len(labs) - 3} more")

if __name__ == '__main__':
    check_institution_naming()