import unittest
import tempfile
import threading
import math
import hashlib
from pathlib import Path
from handoff import Runner,DemoAdapter,Receipt,STAGES
from rgbd_cache import LatestPair,Pair
from analyze_errors import summarize,point_errors
from firmware_preflight import check

class Examples(unittest.TestCase):
    def test_panel_outlives_client_and_reset(self):
        import time
        from panel import Model
        m=Model();m.start()
        with self.assertRaises(ValueError):m.start()
        with self.assertRaises(ValueError):m.reset()
        deadline=time.monotonic()+5
        while m.status()['active'] and time.monotonic()<deadline:time.sleep(.02)
        self.assertEqual(m.status()['result']['state'],'completed')
        m.reset();self.assertIsNone(m.status()['result'])

    def test_five_steps_once(self):
        a=DemoAdapter(delay=0);r=Runner(a);self.assertEqual(r.run()['state'],'completed');self.assertEqual(a.calls,list(STAGES))
        with self.assertRaises(RuntimeError):r.run()
    def test_failure_does_not_grasp(self):
        a=DemoAdapter('drive',0);r=Runner(a).run();self.assertEqual(a.calls,['observe','plan','drive']);self.assertTrue(r['stop_acknowledged'])
    def test_cancel_during_stage(self):
        class A(DemoAdapter):
            def perform(self,stage,rid,cancel):cancel.set();return Receipt(rid,stage,True)
        r=Runner(A()).run();self.assertEqual(r['state'],'cancelled');self.assertEqual(len(r['events']),1)
    def test_old_receipt_rejected(self):
        class A(DemoAdapter):
            def perform(self,stage,rid,cancel):return Receipt('old',stage,True)
            def stop(self):raise RuntimeError('lost')
        r=Runner(A()).run();self.assertEqual(r['state'],'failed');self.assertFalse(r['stop_acknowledged'])
    def test_pre_request_cache_can_be_fresh(self):
        c=LatestPair();c.publish(Pair(9.95,9.96,'boot',b'r',b'd'));self.assertEqual(c.get(10,'boot').rgb,b'r')
        with self.assertRaises(ValueError):c.get(10,'boot',not_before=9.97)
    def test_bad_time_domains(self):
        c=LatestPair();c.publish(Pair(9.95,9.96,'boot',b'r',b'd'))
        for now,clock in [(11,'boot'),(9,'boot'),(10,'other')]:
            with self.assertRaises(ValueError):c.get(now,clock)
    def test_skew(self):
        c=LatestPair();c.publish(Pair(9.5,9.9,'b',b'r',b'd'))
        with self.assertRaises(ValueError):c.get(10,'b')
    def test_wrapped_heading(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'x.csv';p.write_text('time_s,gyro_z_rad_s,yaw_rad\n0,0.02,3.13\n1,0.02,-3.133185307179586\n')
            self.assertAlmostEqual(summarize(p)['yaw_change_deg'],math.degrees(.02))
            p.write_text('time_s,gyro_z_rad_s,yaw_rad\n0,nan,0\n1,0,0\n')
            with self.assertRaises(ValueError):summarize(p)
    def test_known_point_error(self):
        r=point_errors('examples/synthetic_points.csv');self.assertAlmostEqual(r['rms_3d_error_m'],.01)
    def test_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'example.txt';p.write_bytes(b'abc');self.assertTrue(check(p,hashlib.sha256(b'abc').hexdigest())['matches']);self.assertFalse(check(p,'0'*64)['matches'])

if __name__=='__main__':unittest.main()
