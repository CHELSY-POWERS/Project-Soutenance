"""
Simple scoring system for log events
Works independently of NSL-KDD models
Uses rule-based + statistical scoring
"""

class LogScorer:
    """
    Scores log events based on rules and patterns
    This replaces NSL-KDD models for log-specific detection
    """

    # Threat scores for each event type
    THREAT_SCORES = {
        'failed_login':      0.7,
        'invalid_user':      0.8,
        'successful_login':  0.1,
        'sudo_command':      0.4,
        'web_request':       0.1,
        'memory_exhaustion': 0.6,
        'crash':             0.5,
        'kernel_error':      0.5,
        'service_failure':   0.4,
        'unknown':           0.2,
    }

    def score_event(self, event):
        """
        Score a single log event
        Returns score between 0 (safe) and 1 (dangerous)
        """
        base_score = self.THREAT_SCORES.get(event.get('event_type', 'unknown'), 0.2)

        # Boost score based on specific indicators
        if event.get('is_root_attempt'):
            base_score = min(base_score + 0.3, 1.0)

        if event.get('is_invalid_user'):
            base_score = min(base_score + 0.2, 1.0)

        if event.get('is_suspicious'):
            base_score = min(base_score + 0.4, 1.0)

        if event.get('failed_logins', 0) > 0:
            base_score = min(base_score + 0.2, 1.0)

        severity = event.get('severity', 0)
        base_score = min(base_score + (severity * 0.05), 1.0)

        return round(base_score, 3)

    def classify_event(self, event):
        """
        Full classification of a log event
        Returns prediction and threat level
        """
        score = self.score_event(event)

        if score >= 0.7:
            prediction  = 'anomaly'
            threat_level = 'HIGH'
        elif score >= 0.4:
            prediction  = 'suspicious'
            threat_level = 'MEDIUM'
        else:
            prediction  = 'normal'
            threat_level = 'LOW'

        return {
            'prediction':   prediction,
            'anomaly_score': score,
            'threat_level': threat_level,
            'is_anomaly':   score >= 0.4
        }
