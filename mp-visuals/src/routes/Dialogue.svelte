
<script lang="ts">
    import { flip } from 'svelte/animate';
    import { expoInOut } from 'svelte/easing';
    import { slide } from 'svelte/transition';
    import { writable, get } from 'svelte/store';
    import type { Action } from './interfaces';
    import { PHASES, ACTIONS, IGNORED_ACTIONS } from './consts';
    import { convert_to_string } from './action_queue.ts';
    let { action }: { action:Action | undefined } = $props();

    const log = writable<string[]>([]);
    const phase = writable<keyof typeof PHASES>();
    const prev_action = writable<keyof typeof ACTIONS | undefined>();
    function add_to_log(action_: Action | undefined){
      
      if(action_ == undefined) return '';

      if(IGNORED_ACTIONS.includes(action_.action)) return '';

      const phrase = convert_to_string(action_)
      

      const prev_phase = get(phase);

      if(action?.snapshot.phase === PHASES.GAME_START) {
        if(get(prev_action) != action?.action) {
          console.log("Hello?");
          log.set([...get(log), ` `])
        }
      }

      prev_action.set(action?.action);

      if(action_.snapshot.phase !== prev_phase) {
        const title = `\n${action_.snapshot.phase.toUpperCase()}\n\n`;
        log.set([...get(log), title])
      }

      phase.set(action_.snapshot.phase);

      log.set([...get(log), phrase]);
      return get(log);
    }

	$effect(() => {
    add_to_log(action);

  });

</script>


<div class="dialogue">
  <ul class="log">
    {#each $log as a, index (index)}
    <li transition:slide={{easing: expoInOut, duration: 125}} class="log">{a}</li>
    {/each}
  </ul>
</div>


<style>

.log {
  width: auto;
  list-style-type: none;
  white-space: pre-wrap;
  text-indent: -2cqw;
  overflow-wrap: break-word;
}

.dialogue {
  -webkit-mask-image: linear-gradient(to top, black 50%, transparent 90%);
  mask-image: linear-gradient(to top, black 50%, transparent 90%);
  display: flex;
  height: 100%;
  width: 100%;
  overflow: hidden;
  flex-direction: column;
  justify-content: flex-end;
  white-space: pre-line;
  color:white;
  font-family: 'Apple SD Gothic Neo';
  text-align: left;
  font-size: 1.5cqw;
  font-weight: 100;
}

.icon {
  position: absolute;
  background-color: #111;
  border-style: dotted;
  height: 11.5cqw;
  aspect-ratio: 1;
  top: 41.9cqw;
  left: 67cqw;
  border-radius: 50%;
}


</style>