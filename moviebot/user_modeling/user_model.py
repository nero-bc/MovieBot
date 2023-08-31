"""Class for user modeling."""


import json
import os
from collections import defaultdict
from typing import Dict, List

from moviebot.database.database import DataBase


class UserModel:
    def __init__(self, user_id: str, historical_movie_choices_path: str = None):
        """Initializes the user model.

        The JSON file with historical movie choices is a dictionary with the
        movie id as key and the list of choices as value.

        Args:
            user_id: User id.
            historical_movie_choices_path: Path to the JSON file with historical
              movie choices. Defaults to None.
        """
        self.user_id = user_id
        self._movies_choices = defaultdict(list)

        if historical_movie_choices_path and os.path.exists(
            historical_movie_choices_path
        ):
            # Load historical movie choices
            movie_choices = json.load(open(historical_movie_choices_path, "r"))
            self._movies_choices.update(movie_choices)

        self.tag_preferences = defaultdict(lambda: defaultdict(float))

    @property
    def movie_choices(self) -> Dict[str, str]:
        """Returns user 's movie choices."""
        return self._movies_choices

    def update_movie_choice(self, movie_id: str, choice: str) -> None:
        """Updates the choices for a given user.

        Args:
            movie_id: Id of the movie.
            choice: User choice (i.e., accept, reject).
        """
        self._movies_choices[movie_id].append(choice)

    def update_movies_choices(self, movies_choices: Dict[str, str]) -> None:
        """Updates the movie choices for a given user.

        Args:
            movies_choices: Dictionary with movie choices (i.e., accept,
              reject).
        """
        self._movies_choices.update(movies_choices)

    def get_movie_choices(self, movie_id: str) -> List[str]:
        """Returns the choices for a given movie.

        Args:
            movie_id: Id of the movie.

        Returns:
            List of previous choices for a movie.
        """
        return self._movies_choices[movie_id]

    def _convert_choice_to_preference(self, choice: str) -> float:
        """Converts a choice to a preference within the range [-1,1].

        Dislike is represented by a preference below 0, while like is
        represented by a preference above 0. If the choice does not express a
        preference (i.e., inquire), then the preference is neutral, i.e., 0.
        Possible choices are: accept, reject, dont_like, inquire, and watched.

        Args:
            choice: Choice (i.e., accept, reject).

        Returns:
            Preference within the range [-1,1].
        """
        if choice == "accept":
            return 1.0
        elif choice in ["reject", "dont_like"]:
            return -1.0

        return 0.0

    def compute_tag_preference(
        self, slot: str, tag: str, database: DataBase
    ) -> str:
        """Computes the preference for a given tag (e.g., comedies).

        Args:
            slot: Slot name.
            tag: Tag.
            database: Database with all the movies.

        Returns:
            Tag preference.
        """
        sql_cursor = database.sql_connection.cursor()
        tag_set = sql_cursor.execute(
            f"SELECT ID FROM {database._get_table_name()} WHERE {slot} LIKE "
            f"'%{tag}%'"
        ).fetchall()

        preference = 0.0
        count_rated = 0
        for movie_id, choices in self._movies_choices.items():
            if movie_id in tag_set:
                # TODO: decide how to handle contradictory choices (e.g., the
                # same movie was accepted and rejected)
                for choice in choices:
                    preference += self._convert_choice_to_preference(choice)
                    count_rated += 1

        return preference / count_rated if count_rated > 0 else 0.0

    def get_tag_preference(self, slot: str, tag: str) -> float:
        """Returns the preference for a given tag (e.g., comedies).

        If the preference is not explicitly set, then it is computed based on
        movies choices.

        Args:
            slot: Slot name.
            tag: Tag.

        Returns:
            Preference.
        """
        preference = self.tag_preferences[slot].get(tag, None)
        if preference is None:
            return self.compute_tag_preference(slot, tag)
        return preference

    def set_tag_preference(
        self, slot: str, tag: str, preference: float
    ) -> None:
        """Sets the preference for a given tag (e.g., comedies).

        Args:
            slot: Slot name.
            tag: Tag.
            preference: Preference.
        """
        self.tag_preferences[slot][tag] = preference
