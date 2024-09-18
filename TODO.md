# TODO: Implement JSON Output for Game Assistant

1. Update `play_game` route in `app/damath/controller.py`:
   - Modify the response handling to expect JSON output from the game assistant.
   - Ensure the route returns the JSON response directly to the client.

2. Modify the game assistant's output processing:
   - Implement a function to parse the assistant's response into a JSON structure.
   - Handle potential errors in JSON parsing gracefully.

3. Update client-side code to handle JSON responses:
   - Modify any frontend code that processes the game assistant's responses to expect JSON.
   - Implement logic to extract 'message' and 'action' from the JSON response.

4. Test the new JSON output format:
   - Create unit tests for JSON response parsing.
   - Perform integration tests to ensure proper communication between frontend and backend.
