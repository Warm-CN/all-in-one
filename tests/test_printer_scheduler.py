"""Printer lifecycle worker management without a live database."""
import asyncio
import unittest
from unittest.mock import patch
from app import main


class PrinterSchedulerTests(unittest.IsolatedAsyncioTestCase):
    async def test_worker_sweeps_and_stops_without_dangling_task(self):
        stop = asyncio.Event()
        calls = []
        def sweep():
            calls.append("swept")
        with patch.object(main, "sweep_printer_lifecycle", side_effect=sweep):
            task = asyncio.create_task(main.printer_lifecycle_loop(stop))
            for _ in range(100):
                if calls:
                    break
                await asyncio.sleep(0.001)
            self.assertEqual(calls, ["swept"])
            stop.set()
            await asyncio.wait_for(task, timeout=1)
            self.assertTrue(task.done())

    async def test_worker_logs_failure_and_can_shutdown(self):
        stop = asyncio.Event()
        def failing_sweep():
            stop.set()
            raise RuntimeError("test database unavailable")
        with patch.object(main, "sweep_printer_lifecycle", side_effect=failing_sweep):
            with self.assertLogs("app.main", level="ERROR"):
                await main.printer_lifecycle_loop(stop)
        self.assertTrue(stop.is_set())
