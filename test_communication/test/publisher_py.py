# Copyright 2016 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import importlib
import os
import sys
import time

import rclpy
from rclpy.qos import qos_profile_default
from rclpy.qos import QoSReliabilityPolicy

# this is needed to allow import of test_communication messages
sys.path.insert(0, os.getcwd())


def talker(message_name, number_of_cycles, qos_profile):
    from message_fixtures import get_test_msg

    message_pkg = 'test_communication'
    module = importlib.import_module(message_pkg + '.msg')
    msg_mod = getattr(module, message_name)

    rclpy.init([])

    node = rclpy.create_node('talker')

    chatter_pub = node.create_publisher(
        msg_mod, 'test_message_' + message_name, qos_profile)

    cycle_count = 0
    print('talker: beginning loop')
    msgs = get_test_msg(message_name)
    while rclpy.ok() and cycle_count < number_of_cycles:
        msg_count = 0
        for msg in msgs:
            chatter_pub.publish(msg)
            msg_count += 1
            print('publishing message #%d' % msg_count)
            time.sleep(0.01)
        cycle_count += 1
        time.sleep(0.1)
    rclpy.shutdown()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('message_name', default='Primitives',
                        help='name of the ROS message')
    parser.add_argument('-n', '--number_of_cycles', type=int, default=100,
                        help='number of sending attempts')
    parser.add_argument('qos_reliability', default='reliable', nargs='?',
                        help='QoS reliability policy (reliable or best_effort)')
    args = parser.parse_args()

    qos_profile = qos_profile_default
    if args.qos_reliability == 'best_effort':
        qos_profile.reliability = QoSReliabilityPolicy.RMW_QOS_POLICY_RELIABILITY_BEST_EFFORT
    else:
        qos_profile.reliability = QoSReliabilityPolicy.RMW_QOS_POLICY_RELIABILITY_RELIABLE

    try:
        talker(
            message_name=args.message_name,
            number_of_cycles=args.number_of_cycles,
            qos_profile=qos_profile,
        )
    except KeyboardInterrupt:
        print('talker stopped cleanly')
    except BaseException:
        print('exception in talker:', file=sys.stderr)
        raise
