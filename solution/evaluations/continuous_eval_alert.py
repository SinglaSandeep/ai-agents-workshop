"""Create an Azure Monitor metric alert on the continuous-eval pass rate.

Fires when the rolling pass rate drops below 80% for 30 minutes.

Usage:
    python -m solution.evaluations.continuous_eval_alert
"""

from __future__ import annotations

import os

from azure.identity import DefaultAzureCredential
from azure.mgmt.monitor import MonitorManagementClient

from src.common.settings import get_settings


def main() -> None:
    settings = get_settings()
    sub_id = settings.azure_subscription_id
    rg = settings.azure_resource_group

    if not sub_id or not rg:
        raise RuntimeError("AZURE_SUBSCRIPTION_ID and AZURE_RESOURCE_GROUP are required.")

    target_resource_id = os.environ.get(
        "APPINSIGHTS_RESOURCE_ID",
        f"/subscriptions/{sub_id}/resourceGroups/{rg}/providers/microsoft.insights/components/zava-appi",
    )

    client = MonitorManagementClient(DefaultAzureCredential(), sub_id)
    alert = client.metric_alerts.create_or_update(
        rg,
        "marketing-quality-low",
        parameters={
            "location": "global",
            "description": "Marketing-agent continuous-eval pass rate below 80%.",
            "severity": 2,
            "enabled": True,
            "scopes": [target_resource_id],
            "evaluation_frequency": "PT5M",
            "window_size": "PT30M",
            "criteria": {
                "odata.type": "Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria",
                "all_of": [
                    {
                        "name": "PassRate",
                        "metric_name": "azure_ai_evaluation/pass_rate",
                        "operator": "LessThan",
                        "threshold": 0.8,
                        "time_aggregation": "Average",
                        "dimensions": [
                            {"name": "agent_name", "operator": "Include",
                             "values": [settings.marketing_agent_name]}
                        ],
                    }
                ],
            },
        },
    )
    print(f"Alert: {alert.id}")


if __name__ == "__main__":
    main()
