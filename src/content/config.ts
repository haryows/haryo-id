import { defineCollection, z } from 'astro:content';

const blog = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    date: z.date(),
    category: z.string(),
    // Full URL to the image on your Cloudflare R2 public bucket / custom domain,
    // e.g. https://media.haryo.id/posts/security-headers.png
    image: z.string().optional(),
    draft: z.boolean().optional().default(false),
  }),
});

export const collections = { blog };
