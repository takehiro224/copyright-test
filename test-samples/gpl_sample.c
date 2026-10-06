                             quoteaf (infile));
                      newlines2 = newlines;
                      return false;
                    }
                }
              if (n_to_read != 0)
                input_pending = true;
#endif

              if (!input_pending)
                write_pending (outbuf, &bpout);

              /* Read more input into INBUF.  */

              size_t n_read = safe_read (input_desc, inbuf, insize);
              if (n_read == SAFE_READ_ERROR)
                {
                  error (0, errno, "%s", quotef (infile));
                  write_pending (outbuf, &bpout);
                  newlines2 = newlines;
                  return false;
                }
              if (n_read == 0)
                {
                  write_pending (outbuf, &bpout);
                  newlines2 = newlines;
                  return true;
                }

              /* Update the pointers and insert a sentinel at the buffer
                 end.  */

              bpin = inbuf;
              eob = bpin + n_read;
              *eob = '\n';
            }
          else
            {
              /* It was a real (not a sentinel) newline.  */

              /* Was the last line empty?
                 (i.e., have two or more consecutive newlines been read?)  */

              if (++newlines > 0)
                {
                  if (newlines >= 2)
                    {
                      /* Limit this to 2 here.  Otherwise, with lots of
                         consecutive newlines, the counter could wrap
                         around at INT_MAX.  */
                      newlines = 2;

                      /* Are multiple adjacent empty lines to be substituted
                         by single ditto (-s), and this was the second empty
                         line?  */
                      if (squeeze_blank)
                        {
                          ch = *bpin++;
                          continue;
                        }
                    }

                  /* Are line numbers to be written at empty lines (-n)?  */

                  if (number && !number_nonblank)
                    {
                      next_line_num ();
                      bpout = stpcpy (bpout, line_num_print);
                    }
                }

              /* Output a currency symbol if requested (-e).  */
              if (show_ends)
                {
                  if (pending_cr)
                    {
                      *bpout++ = '^';
                      *bpout++ = 'M';
                      pending_cr = false;
                    }
                  *bpout++ = '$';
                }

              /* Output the newline.  */

              *bpout++ = '\n';
            }
          ch = *bpin++;
        }
      while (ch == '\n');

      /* Here CH cannot contain a newline character.  */

      if (pending_cr)
        {
          *bpout++ = '\r';
          pending_cr = false;
        }

      /* Are we at the beginning of a line, and line numbers are requested?  */

