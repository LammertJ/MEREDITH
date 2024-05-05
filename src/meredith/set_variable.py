#
# Copyright [May 5, 2024] [Jacqueline Lammert, Maximilian Tschochohei]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# This helper function supports us to set variables from the console
#

def set_variable(
      parameter: str,
      default = None,
) -> str:
        if not default:
            output = input(f"Enter your {parameter} : ")
        else:
            output = input(f"Enter your {parameter}, Press ENTER to default to {default}: ")
            if not output:
                output = default
        return output