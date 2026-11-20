# Workout coach

Deploy this Edge Function to the same Supabase project used by the workout tracker. Set these Function Secrets in the Supabase dashboard before deploying.

- `OPENAI_API_KEY` is an OpenAI project API key.
- `WORKOUT_COACH_CODE` is a private, randomly generated access code (24 to 256 characters). Enter it in the coach form when requesting a review. Share it only with people authorized to use the API budget.
- `WORKOUT_COACH_MODEL` optionally overrides the default model, `gpt-4.1-mini`.

From the repository root, deploy with the Supabase CLI after signing in.

```sh
supabase functions deploy workout-coach --project-ref wxpgpaepvkbieryeihpb --no-verify-jwt
```

The tracker uses a publishable key and has no user sign-in. This function checks the private coach code before making a billable model request. Keep the OpenAI key and coach code in Function Secrets. Rotate the code if shared inadvertently.

The function receives only completed, nonzero weighted working sets from up to 12 sessions plus the selected goal and effort. It submits the review with Responses API storage disabled and returns plain text. The app displays the advice for review and leaves the workout plan and log untouched.
