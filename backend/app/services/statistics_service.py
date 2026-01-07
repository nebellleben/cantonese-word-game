from typing import Optional, List
from uuid import UUID
from collections import defaultdict
from datetime import date
from app.db.database_service import DatabaseService
from app.api.models.schemas import GameStatistics, ScoreByDate, WrongWord, Student


class StatisticsService:
    """Service for statistics operations."""
    
    def __init__(self, db_service: DatabaseService):
        self.db = db_service
    
    def get_statistics(
        self,
        user_id: UUID,
        target_user_id: Optional[UUID] = None,
        deck_id: Optional[UUID] = None
    ) -> GameStatistics:
        """Get game statistics for a user."""
        # Determine which user's stats to get
        stats_user_id = target_user_id if target_user_id else user_id
        
        # Get all completed sessions for the user
        all_sessions = [
            session for session in self.db.game_sessions.values()
            if session["user_id"] == stats_user_id
            and session["ended_at"] is not None
            and (deck_id is None or session["deck_id"] == deck_id)
        ]
        
        # Calculate basic stats
        total_games = len(all_sessions)
        scores = [session["score"] for session in all_sessions if session["score"] is not None]
        
        if scores:
            average_score = sum(scores) / len(scores)
            best_score = max(scores)
        else:
            average_score = 0.0
            best_score = 0
        
        # Get streak data
        streak_data = self.db.get_user_streak(stats_user_id)
        current_streak = streak_data["current_streak"]
        longest_streak = streak_data["longest_streak"]
        
        # Get scores by date
        scores_by_date_dict = defaultdict(list)
        for session in all_sessions:
            if session["score"] is not None:
                session_date = session["ended_at"].date()
                scores_by_date_dict[session_date].append(session["score"])
        
        scores_by_date = [
            ScoreByDate(date=date_key, score=int(sum(scores) / len(scores)))
            for date_key, scores in sorted(scores_by_date_dict.items())
        ]
        
        # Get top wrong words
        attempts = self.db.get_attempts_by_user(stats_user_id, deck_id)
        # #region agent log
        import json
        with open('/Users/kelvinchan/dev/test/cantonese-word-game/.cursor/debug.log', 'a') as f:
            f.write(json.dumps({"location":"statistics_service.py:62","message":"get_statistics attempts retrieved","data":{"attempts_count":len(attempts),"deck_id":str(deck_id) if deck_id else None},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"D,E"})+"\n")
        # #endregion
        top_wrong_words = self._calculate_wrong_words(attempts)
        # #region agent log
        with open('/Users/kelvinchan/dev/test/cantonese-word-game/.cursor/debug.log', 'a') as f:
            f.write(json.dumps({"location":"statistics_service.py:64","message":"get_statistics top_wrong_words calculated","data":{"top_wrong_words_count":len(top_wrong_words),"first_word":dict(top_wrong_words[0]) if top_wrong_words else None},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"A,B,D"})+"\n")
        # #endregion
        
        return GameStatistics(
            totalGames=total_games,
            averageScore=average_score,
            bestScore=best_score,
            currentStreak=current_streak,
            longestStreak=longest_streak,
            scoresByDate=scores_by_date,
            topWrongWords=top_wrong_words[:20]  # Top 20
        )
    
    def get_students(self, user_id: UUID, user_role: str) -> List[Student]:
        """Get list of students."""
        if user_role == "admin":
            # Admin sees all students
            students = self.db.get_all_students()
        elif user_role == "teacher":
            # Teacher sees only associated students
            student_ids = self.db.get_students_by_teacher(user_id)
            students = [self.db.get_user_by_id(sid) for sid in student_ids if self.db.get_user_by_id(sid)]
        else:
            # Students cannot access this
            return []
        
        # Calculate stats for each student
        result = []
        for student in students:
            streak_data = self.db.get_user_streak(student["id"])
            
            # Calculate total score
            student_sessions = [
                s for s in self.db.game_sessions.values()
                if s["user_id"] == student["id"] and s["score"] is not None
            ]
            total_score = sum(s["score"] for s in student_sessions)
            
            result.append(Student(
                id=student["id"],
                username=student["username"],
                streak=streak_data["current_streak"],
                totalScore=total_score
            ))
        
        return result
    
    def get_word_error_ratios(self, user_id: UUID, user_role: str) -> List[WrongWord]:
        """Get word error ratios."""
        if user_role == "admin":
            # Admin sees all errors - get all attempts
            # We need to get attempts from all users
            all_students = self.db.get_all_students()
            student_ids = [UUID(s["id"]) for s in all_students]
            attempts = self.db.get_attempts_by_students(student_ids) if student_ids else []
        elif user_role == "teacher":
            # Teacher sees errors from their students
            student_ids = self.db.get_students_by_teacher(user_id)
            attempts = self.db.get_attempts_by_students(student_ids) if student_ids else []
        else:
            # Students see their own errors
            attempts = self.db.get_attempts_by_user(user_id)
        
        return self._calculate_wrong_words(attempts)
    
    def _calculate_wrong_words(self, attempts: List[dict]) -> List[WrongWord]:
        """Calculate wrong word statistics from attempts."""
        # #region agent log
        import json
        with open('/Users/kelvinchan/dev/test/cantonese-word-game/.cursor/debug.log', 'a') as f:
            f.write(json.dumps({"location":"statistics_service.py:127","message":"_calculate_wrong_words entry","data":{"attempts_count":len(attempts)},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"D"})+"\n")
        # #endregion
        word_stats = defaultdict(lambda: {"correct": 0, "incorrect": 0})
        
        for attempt in attempts:
            word_id = attempt["word_id"]
            if attempt["is_correct"]:
                word_stats[word_id]["correct"] += 1
            else:
                word_stats[word_id]["incorrect"] += 1
        
        wrong_words = []
        for word_id, stats in word_stats.items():
            word = self.db.get_word(word_id)
            if not word:
                continue
            
            total_attempts = stats["correct"] + stats["incorrect"]
            wrong_count = stats["incorrect"]
            ratio = wrong_count / total_attempts if total_attempts > 0 else 0.0
            
            wrong_word = WrongWord(
                wordId=word_id,
                word=word["text"],
                wrongCount=wrong_count,
                totalAttempts=total_attempts,
                ratio=ratio
            )
            # #region agent log
            with open('/Users/kelvinchan/dev/test/cantonese-word-game/.cursor/debug.log', 'a') as f:
                f.write(json.dumps({"location":"statistics_service.py:154","message":"_calculate_wrong_words WrongWord created","data":{"word_id":str(word_id),"word":word["text"],"wrongCount":wrong_count,"ratio":ratio,"wrongWord_dict":wrong_word.model_dump()},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"A"})+"\n")
            # #endregion
            wrong_words.append(wrong_word)
        
        # Sort by error ratio (descending)
        wrong_words.sort(key=lambda x: x.ratio, reverse=True)
        # #region agent log
        with open('/Users/kelvinchan/dev/test/cantonese-word-game/.cursor/debug.log', 'a') as f:
            f.write(json.dumps({"location":"statistics_service.py:158","message":"_calculate_wrong_words return","data":{"wrong_words_count":len(wrong_words),"first_word_dict":wrong_words[0].model_dump() if wrong_words else None},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"A,B"})+"\n")
        # #endregion
        return wrong_words

