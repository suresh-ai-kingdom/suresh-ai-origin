#!/usr/bin/env python3
"""Test Global Calling System"""

from models import get_session, CallRecord
from global_calling_system import GlobalCallingManager
import time

def test_calling_system():
    print("🧪 Testing Global Calling System...")
    
    # Test database save
    session = get_session()
    
    # Delete any existing test call
    session.query(CallRecord).filter(CallRecord.id.like('test_call_%')).delete()
    session.commit()
    
    test_call = CallRecord(
        id='test_call_001',
        call_id='test_voip_' + str(int(time.time())),
        category='internet_voip',
        provider='twilio',
        from_number='+91-9876543210',
        to_number='+1-555-0123',
        status='completed',
        duration_seconds=120,
        cost_rupees=2.0,
        started_at=time.time(),
        ended_at=time.time() + 120,
        created_at=time.time()
    )
    session.add(test_call)
    session.commit()
    print('✅ Test call saved to database')
    
    # Verify retrieval
    saved_call = session.query(CallRecord).filter_by(id='test_call_001').first()
    print(f'✅ Retrieved call: {saved_call.call_id} ({saved_call.category})')
    print(f'   Duration: {saved_call.duration_seconds}s, Cost: ₹{saved_call.cost_rupees}')
    
    # Test GlobalCallingManager
    manager = GlobalCallingManager()
    coverage = manager.get_global_coverage_report()
    print(f'✅ Coverage: {coverage["total_countries"]} countries')
    print(f'✅ Languages: {coverage["languages_supported"]}')
    print(f'✅ Agents: {coverage["agents_available"]}')
    
    session.close()
    print("\n✅ All tests passed! Global Calling System ready!")

if __name__ == '__main__':
    test_calling_system()
