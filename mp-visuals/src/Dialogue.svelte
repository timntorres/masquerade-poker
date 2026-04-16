
<script lang="ts">
    let { dialogue }: { dialogue:string } = $props();
</script>


<div class="dialogue">
    { dialogue }
</div>


<div class="icon">
</div>

<style>
.dialogue {
  padding: 4cqw;
  color:white;
  font-family: 'Apple SD Gothic Neo';
  text-align: left;
  font-size: 1.8cqw;
  font-weight: 700;
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