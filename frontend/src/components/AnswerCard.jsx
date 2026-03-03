export default function AnswerCard({ answer }) {
  return (
    <div className="right-panel">
      {answer ? (
        <div className="answer-box">
          {answer}
        </div>
      ) : (
        <div className="placeholder-box">
          Your answer will appear here...
        </div>
      )}
    </div>
  );
}