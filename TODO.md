# TODO: Implement JSON Output for Game Assistant

1. Update `play_game` route in `app/damath/controller.py`:
   - Modify the response handling to expect JSON output from the game assistant.
   - Ensure the route returns the JSON response directly to the client.

2. Modify the game assistant's output processing:
   - Implement a function to parse the assistant's response into a JSON structure.
   - Handle potential errors in JSON parsing gracefully.

3. Test the new JSON output format:
   - Create unit tests for JSON response parsing.
   - Perform integration tests to ensure proper communication between frontend and backend.


Problem:
add_references_to_prompt=True
includes knowledge base and returns the reference not the guided instruction.
Solution: