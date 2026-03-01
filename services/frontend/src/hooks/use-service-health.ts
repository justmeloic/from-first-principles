/**
 * Copyright 2025 Loïc Muhirwa
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { useCallback, useEffect, useRef, useState } from "react";

export type ServiceStatus = "available" | "unavailable" | "checking";

/**
 * Hook that periodically pings a health endpoint and tracks whether
 * the service is reachable.
 *
 * @param healthCheckFn - An async function that calls the API.
 *   It should throw on failure and resolve on success.
 * @param interval - Polling interval in ms (default 120 000).
 */
export function useServiceHealth(
  healthCheckFn: () => Promise<unknown>,
  interval = 120_000
) {
  const [status, setStatus] = useState<ServiceStatus>("checking");
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const checkHealth = useCallback(async () => {
    try {
      await healthCheckFn();
      setStatus("available");
    } catch {
      setStatus("unavailable");
    }
  }, [healthCheckFn]);

  useEffect(() => {
    checkHealth();
    intervalRef.current = setInterval(checkHealth, interval);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [checkHealth, interval]);

  return { status, retry: checkHealth };
}
