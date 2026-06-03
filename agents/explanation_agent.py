class ExplanationAgent:

    def generate_explanation(self, explanations):

        result = "\nXAI Explanation:\n"

        for exp in explanations:

            result += f"- {exp}\n"

        return result