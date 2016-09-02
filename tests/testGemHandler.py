#####################################################################
# testGemHandler.py
#
# (c) Copyright 2013-2016, Benjamin Parzella. All rights reserved.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#####################################################################

import unittest

import secsgem

from testconnection import HsmsTestServer

class GemHandlerPassiveGroup(object):
    def testConstructor(self):
        self.assertIsNotNone(self.client)

        print self.client    # cover repr and _serialize_data

    def testEnableDisable(self):
        self.assertEqual(self.client.communicationState.current, "NOT_COMMUNICATING")

        self.server.stop()
        self.client.disable()

        self.assertEqual(self.client.communicationState.current, "DISABLED")

        self.server.start()
        self.client.enable()

        self.assertEqual(self.client.communicationState.current, "NOT_COMMUNICATING")
        
    def testConnection(self):
        self.server.simulate_connect()

        system_id = self.server.get_next_system_counter()
        self.server.simulate_packet(secsgem.HsmsPacket(secsgem.HsmsSelectReqHeader(system_id)))

        packet = self.server.expect_packet(system_id=system_id)

        self.assertIsNot(packet, None)
        self.assertEqual(packet.header.sType, 0x02)
        self.assertEqual(packet.header.sessionID, 0xffff)

        self.assertEqual(self.client.communicationState.current, "WAIT_CRA")

    def establishCommunication(self):
        self.server.simulate_connect()

        system_id = self.server.get_next_system_counter()
        self.server.simulate_packet(secsgem.HsmsPacket(secsgem.HsmsSelectReqHeader(system_id)))

        packet = self.server.expect_packet(system_id=system_id)

        packet = self.server.expect_packet(function=13)

        self.server.simulate_packet(self.server.generate_stream_function_packet(packet.header.system, secsgem.SecsS01F14([0])))
       
    def testReceivingS01F13(self):
        self.server.simulate_connect()

        system_id = self.server.get_next_system_counter()
        self.server.simulate_packet(secsgem.HsmsPacket(secsgem.HsmsSelectReqHeader(system_id)))

        packet = self.server.expect_packet(system_id=system_id)

        self.assertIsNot(packet, None)
        self.assertEqual(packet.header.sType, 0x02)
        self.assertEqual(packet.header.sessionID, 0xffff)

        self.assertEqual(self.client.communicationState.current, "WAIT_CRA")

        packet = self.server.expect_packet(function=13)

        self.assertIsNot(packet, None)
        self.assertEqual(packet.header.sType, 0x00)
        self.assertEqual(packet.header.sessionID, 0x0)
        self.assertEqual(packet.header.stream, 0x01)
        self.assertEqual(packet.header.function, 0x0d)

        self.assertEqual(self.client.communicationState.current, "WAIT_CRA")

        self.server.simulate_packet(self.server.generate_stream_function_packet(packet.header.system, secsgem.SecsS01F14([0])))

        self.assertEqual(self.client.communicationState.current, "COMMUNICATING")

    def testSendingS01F13(self):
        self.server.simulate_connect()

        system_id = self.server.get_next_system_counter()
        self.server.simulate_packet(secsgem.HsmsPacket(secsgem.HsmsSelectReqHeader(system_id)))

        packet = self.server.expect_packet(system_id=system_id)

        self.assertIsNot(packet, None)
        self.assertEqual(packet.header.sType, 0x02)
        self.assertEqual(packet.header.sessionID, 0xffff)

        self.assertEqual(self.client.communicationState.current, "WAIT_CRA")

        s01f13ReceivedPacket = self.server.expect_packet(function=13)

        self.assertIsNot(s01f13ReceivedPacket, None)
        self.assertEqual(s01f13ReceivedPacket.header.sType, 0x00)
        self.assertEqual(s01f13ReceivedPacket.header.sessionID, 0x0)
        self.assertEqual(s01f13ReceivedPacket.header.stream, 0x01)
        self.assertEqual(s01f13ReceivedPacket.header.function, 0x0d)

        self.assertEqual(self.client.communicationState.current, "WAIT_CRA")

        system_id = self.server.get_next_system_counter()
        self.server.simulate_packet(self.server.generate_stream_function_packet(system_id, secsgem.SecsS01F13()))

        self.assertEqual(self.client.communicationState.current, "COMMUNICATING")

        packet = self.server.expect_packet(system_id=system_id)

        self.assertIsNot(packet, None)
        self.assertEqual(packet.header.sType, 0x00)
        self.assertEqual(packet.header.sessionID, 0x0)
        self.assertEqual(packet.header.stream, 0x01)
        self.assertEqual(packet.header.function, 0x0e)

        self.assertEqual(self.client.communicationState.current, "COMMUNICATING")

        self.server.simulate_packet(self.server.generate_stream_function_packet(s01f13ReceivedPacket.header.system, secsgem.SecsS01F14([0])))

        self.assertEqual(self.client.communicationState.current, "COMMUNICATING")

class TestGemHandlerPassive(unittest.TestCase, GemHandlerPassiveGroup):
    __testClass = secsgem.GemHandler
    
    def setUp(self):
        self.assertIsNotNone(self.__testClass)

        self.server = HsmsTestServer()

        self.client = self.__testClass("127.0.0.1", 5000, False, 0, "test", None, self.server)

        self.server.start()
        self.client.enable()

    def tearDown(self):
        self.client.disable()
        self.server.stop()
