(function () {
  'use strict';
  const model = window.VectorAddition;
  const view = window.VectorAdditionView;
  const keys = Object.keys(model.defaults);
  let params = { ...model.defaults };
  const status = document.getElementById('status');
  const pair = vector => `(${vector.join(', ')})`;

  function update() {
    const result = model.compute(params);
    for (const key of keys) {
      for (const id of [key, key + '-number']) {
        const field = document.getElementById(id);
        field.value = params[key];
        field.removeAttribute('aria-invalid');
      }
    }
    document.getElementById('diagram').innerHTML = view.svg(result);
    document.getElementById('a-value').textContent = pair(result.a);
    document.getElementById('b-value').textContent = pair(result.b);
    document.getElementById('sum-value').textContent = pair(result.sum);
    document.getElementById('observation').textContent = result.sumZero
      ? '两段位移完全抵消，终点回到原点。零向量用圆环表示，没有方向。'
      : result.aZero || result.bZero
        ? '其中一个向量为零，合向量与另一个向量重合。圆环表示零向量。'
        : `两条相加路径都到达 ${pair(result.sum)}。绿色箭头表示从原点到这里的总位移。`;
    status.textContent = '';
  }

  for (const key of keys) {
    for (const id of [key, key + '-number']) {
      document.getElementById(id).addEventListener('input', event => {
        const input = event.target;
        const value = input.valueAsNumber;
        try {
          if (!input.validity.valid) throw new RangeError('invalid input');
          model.compute({ ...params, [key]: value });
          params = { ...params, [key]: value };
          update();
        } catch (error) {
          if (!(error instanceof RangeError)) throw error;
          input.setAttribute('aria-invalid', 'true');
          status.textContent = '请输入 −3 到 3 之间、步长为 0.5 的分量。图形保留最后一次有效结果。';
        }
      });
    }
  }
  document.getElementById('reset').addEventListener('click', () => {
    params = { ...model.defaults };
    update();
  });
  document.getElementById('cancel').addEventListener('click', () => {
    params = { ax: 2, ay: 1, bx: -2, by: -1 };
    update();
  });
  document.getElementById('zero').addEventListener('click', () => {
    params = { ax: 0, ay: 0, bx: 1, by: 2 };
    update();
  });
  update();
})();
