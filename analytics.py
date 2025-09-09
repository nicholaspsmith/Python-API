import pandas as pd
from sqlalchemy import create_engine
# from datetime import datetime, timedelta
# import json


class TicketAnalytics:
    def __init__(self, database_url: str = "sqlite:///./tickets.db"):
        self.engine = create_engine(database_url)

    def load_tickets_to_dataframe(self) -> pd.DataFrame:
        """Load all tickets into a pandas DataFrame"""
        query = "SELECT * FROM tickets"
        df = pd.read_sql(query, self.engine)
        return df

    def analyze_priority_distribution(self) -> dict:
        """Analyze distribution of ticket priorities"""
        df = self.load_tickets_to_dataframe()

        if df.empty:
            return {"message": "No tickets found"}

        # group by priority & count
        priority_counts = df["priority"].value_counts().to_dict()

        # calculate percentages
        total = len(df)
        priority_percentages = {
            priority: (count / total) * 100
            for priority, count in priority_counts.items()
        }

        return {
            "counts": priority_counts,
            "percentages": priority_percentages,
            "total_tickets": total,
        }

    def analyze_token_usage(self) -> dict:
        """Analyze Claude token usage statistics"""
        df = self.load_tickets_to_dataframe()

        # filter only analyzed tickets
        analyzed = df[df["tokens_used"].notna()]

        if analyzed.empty:
            return {"message": "No analyzed tickets found"}

        return {
            "total_tokens": int(analyzed["tokens_used"].sum()),
            "average_tokens_per_ticket": float(analyzed["tokens_used"].mean()),
            "max_tokens_single_ticket": int(analyzed["tokens_used"].max()),
            "min_tokens_single_ticket": int(analyzed["tokens_used"].min()),
            "tickets_analyzed": len(analyzed),
        }

    def time_series_analysis(self) -> dict:
        """Analyze ticket creation patterns over time"""
        df = self.load_tickets_to_dataframe()

        if df.empty:
            return {"message": "No tickets found"}

        df["created_at"] = pd.to_datetime(df["created_at"])

        # group by date
        df["date"] = df["created_at"].dt.date
        daily_counts = df.groupby("date").size().to_dict()

        # convert date objects to strings for json serialization
        daily_counts = {str(k): v for k, v in daily_counts.items()}

        # calculate ticket velocity (avg tickets/day)
        if len(df) > 0:
            date_range = (df["created_at"].max() - df["created_at"].min()).days + 1
            velocity = len(df) / max(date_range, 1)
        else:
            velocity = 0

        return {
            "daily_counts": daily_counts,
            "average_tickets_per_day": velocity,
            "busiest_day": (
                max(daily_counts, key=daily_counts.get) if daily_counts else None
            ),
        }

    def get_summary_statistics(self) -> dict:
        """Get comprehensive summary stats"""
        df = self.load_tickets_to_dataframe()

        if df.empty:
            return {"message": "No tickets found"}

        # use pandas describe for numeric columns
        numeric_stats = df.describe().to_dict() if not df.empty else {}

        # status distribution
        status_dist = df["status"].value_counts().to_dict() if "status" in df else {}

        # priority vs status crosstab
        if "priority" in df and "status" in df:
            crosstab = pd.crosstab(df["priority"], df["status"]).to_dict()
        else:
            crosstab = {}

        return {
            "total_tickets": len(df),
            "numeric_statistics": numeric_stats,
            "status_distribution": status_dist,
            "priority_status_crosstab": crosstab,
        }
