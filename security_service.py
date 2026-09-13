import datetime

class SecurityService:
    """
    Multi-Agency Dispatcher, Offline Storage Sync Manager & Audit Logger
    """
    OFFLINE_QUEUE = []
    AUDIT_LOGS = []

    @staticmethod
    def dispatch_agency_task(agency_type, target_area, task_details):
        """
        Dispatch tactical mission assignment to Police, Fire, Ambulance, or NDRF
        """
        dispatch_record = {
            'dispatch_id': f'DISPATCH-{datetime.datetime.now().strftime("%H%M%S")}',
            'agency': agency_type,
            'target_area': target_area,
            'task_details': task_details,
            'timestamp': datetime.datetime.now().isoformat(),
            'status': 'DISPATCHED'
        }
        SecurityService.AUDIT_LOGS.append(dispatch_record)
        return dispatch_record

    @staticmethod
    def sync_offline_reports(queued_reports):
        """
        Sync offline emergency reports submitted during cellular network outages
        """
        synced_count = 0
        for report in queued_reports:
            SecurityService.OFFLINE_QUEUE.append(report)
            synced_count += 1

        return {
            'synced_count': synced_count,
            'total_queued': len(SecurityService.OFFLINE_QUEUE),
            'status': 'SYNC_COMPLETE'
        }
