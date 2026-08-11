import { defineCollection, z } from 'astro:content';

const blog = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    date: z.date(),
    category: z.string(),
    // Path to the image inside the public/images folder,
    // e.g. /images/security-headers-cover.png
    // (Full URLs also work if you later switch to R2 or another host.)
    image: z.string().optional(),
    draft: z.boolean().optional().default(false),
  }),
});

export const collections = { blog };
