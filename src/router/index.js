import { createRouter, createWebHistory } from "vue-router";
import Classifier from "@/views/Classifier.vue";
import Matcher from "@/views/Matcher.vue";
import Viewer from "@/views/Viewer.vue";
import Cluster from "@/views/Cluster.vue";
import Shop from "@/views/Shop.vue";
import TextLabeler from "@/views/TextLabeler.vue";

const routes = [
  { path: "/", component: Classifier },
  { path: "/matcher", component: Matcher },
  { path: "/viewer", component: Viewer },
  { path: "/cluster", component: Cluster },
  { path: "/shop", component: Shop },
  { path: "/labeler", component: TextLabeler },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
