export function scoreQuiz(spec, answerInput) {
  const answers = answerInput.answers ?? answerInput;
  const dimensions = spec.dimensions;
  const dimensionIds = dimensions.map((dimension) => dimension.id);
  const weights = Object.fromEntries(dimensions.map((dimension) => [dimension.id, Number(dimension.weight ?? 1)]));
  const questionIds = spec.questions.map((question) => question.id);

  const missing = questionIds.filter((questionId) => !(questionId in answers));
  const extras = Object.keys(answers).filter((questionId) => !questionIds.includes(questionId)).sort();
  if (missing.length) throw new Error(`Missing answers: ${missing.join(", ")}`);
  if (extras.length) throw new Error(`Unknown questions: ${extras.join(", ")}`);

  const raw = Object.fromEntries(dimensionIds.map((dimensionId) => [dimensionId, 0]));
  const minimums = Object.fromEntries(dimensionIds.map((dimensionId) => [dimensionId, 0]));
  const maximums = Object.fromEntries(dimensionIds.map((dimensionId) => [dimensionId, 0]));

  for (const question of spec.questions) {
    const selected = question.options.find((option) => option.id === answers[question.id]);
    if (!selected) throw new Error(`Question ${question.id} has no option ${answers[question.id]}`);
    for (const dimensionId of dimensionIds) {
      const values = question.options.map((option) => Number(option.scores?.[dimensionId] ?? 0));
      minimums[dimensionId] += Math.min(...values);
      maximums[dimensionId] += Math.max(...values);
      raw[dimensionId] += Number(selected.scores?.[dimensionId] ?? 0);
    }
  }

  const normalized = {};
  for (const dimensionId of dimensionIds) {
    const range = maximums[dimensionId] - minimums[dimensionId];
    if (range === 0) throw new Error(`Dimension ${dimensionId} has a zero theoretical range`);
    normalized[dimensionId] = (100 * (raw[dimensionId] - minimums[dimensionId])) / range;
  }

  const closeThreshold = Number(spec.scoring?.close_dimension_threshold ?? 15);
  const secondaryThreshold = Number(spec.scoring?.secondary_result_threshold ?? 5);
  const weightSum = Object.values(weights).reduce((sum, weight) => sum + weight, 0);
  const halfUp = (value) => Math.floor(value + 0.5);

  const ranking = spec.results.map((result) => {
    const weightedSum = dimensionIds.reduce((sum, dimensionId) => {
      const difference = normalized[dimensionId] - Number(result.target[dimensionId]);
      return sum + weights[dimensionId] * difference * difference;
    }, 0);
    const distance = Math.sqrt(weightedSum / weightSum);
    const closeDimensions = dimensionIds.filter(
      (dimensionId) => Math.abs(normalized[dimensionId] - Number(result.target[dimensionId])) <= closeThreshold,
    ).length;
    return {
      id: result.id,
      name: result.name,
      match: halfUp(Math.max(0, 100 - distance)),
      distance,
      closeDimensions,
      priority: result.priority,
    };
  });

  ranking.sort((left, right) => {
    const distanceDifference = Number(left.distance.toFixed(12)) - Number(right.distance.toFixed(12));
    if (distanceDifference !== 0) return distanceDifference;
    if (left.closeDimensions !== right.closeDimensions) return right.closeDimensions - left.closeDimensions;
    if (left.priority !== right.priority) return left.priority - right.priority;
    return left.id < right.id ? -1 : left.id > right.id ? 1 : 0;
  });

  const publicRanking = ranking.map(({ id, name, match }) => ({ id, name, match }));
  const primary = publicRanking[0];
  const secondary = publicRanking[1] && primary.match - publicRanking[1].match <= secondaryThreshold
    ? publicRanking[1]
    : null;
  const scores = Object.fromEntries(
    dimensionIds.map((dimensionId) => [dimensionId, halfUp(normalized[dimensionId] * 100) / 100]),
  );
  const evidence = dimensions.map((dimension) => ({
    dimension_id: dimension.id,
    name: dimension.name,
    score: scores[dimension.id],
    lean: scores[dimension.id] >= 50 ? dimension.high_label : dimension.low_label,
  }));

  return { quiz_id: spec.id ?? "quiz", scores, primary, secondary, ranking: publicRanking, evidence };
}
